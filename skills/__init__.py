"""
СберМобайл AI Agent — Skills Registry

Автоматически собирает все skills из доменных папок.
Smart executor с precheck-цепочками.
"""

from skills.account import ALL as ACCOUNT_SKILLS
from skills.tariff import ALL as TARIFF_SKILLS
from skills.services import ALL as SERVICES_SKILLS


# ── SkillContext — состояние на уровне разговора ─────────────

class SkillContext:
    """
    Хранит состояние для одного разговора (сессии).
    """

    def __init__(self):
        self.shown_offers: set = set()

    def mark_offer_shown(self, offer_id) -> None:
        self.shown_offers.add(offer_id)

    def was_offer_shown(self, offer_id) -> bool:
        return offer_id in self.shown_offers


# ── Все skills ──────────────────────────────────────────────

ALL_SKILLS = (
    ACCOUNT_SKILLS
    + TARIFF_SKILLS
    + SERVICES_SKILLS
)

# ── Индексы ─────────────────────────────────────────────────

SKILLS_BY_NAME = {s.name: s for s in ALL_SKILLS}
CONFIRMATION_REQUIRED = {s.name for s in ALL_SKILLS if s.requires_confirmation}
READ_ONLY = {s.name for s in ALL_SKILLS if not s.requires_confirmation}

# ── Precheck chains ─────────────────────────────────────────

PRECHECK_CHAINS = {
    # Будут добавлены по мере обнаружения write-операций
    # "tariff.change": {
    #     "precheck": "tariff.get_current",
    #     "param_map": {},
    # },
}

# ── Группы skills для динамической подгрузки ────────────────

SKILL_GROUPS = {
    "core": [
        "account.get_balance", "account.get_remainders",
        "tariff.get_current", "services.list_current",
    ],
    "tariff": [
        "tariff.get_current", "tariff.list_available",
    ],
    "services": [
        "services.list_current", "services.get_campaigns",
    ],
    "finance": [
        "account.get_balance",
    ],
}

DEFAULT_GROUP = "core"


def get_tools_for_context(groups: list[str] = None, fmt: str = "anthropic") -> list[dict]:
    """
    Получить tools для конкретного контекста.
    Всегда включает core + запрошенные группы.
    """
    groups = groups or []
    names_in_order = []
    seen = set()

    for group_name in [DEFAULT_GROUP] + groups:
        for name in SKILL_GROUPS.get(group_name, []):
            if name not in seen:
                seen.add(name)
                names_in_order.append(name)

    skills = [SKILLS_BY_NAME[n] for n in names_in_order if n in SKILLS_BY_NAME]

    if fmt == "openai":
        return [s.to_openai_tool() for s in skills]
    return [s.to_anthropic_tool() for s in skills]


def get_tools_for_anthropic() -> list[dict]:
    """Все skills в формате Anthropic Tool Use."""
    return [s.to_anthropic_tool() for s in ALL_SKILLS]


def get_tools_for_openai() -> list[dict]:
    """Все skills в формате OpenAI Function Calling."""
    return [s.to_openai_tool() for s in ALL_SKILLS]


# ── Smart Executor ──────────────────────────────────────────

def execute_skill(
    skill_name: str,
    client,
    params: dict,
    confirm_fn=None,
    context: SkillContext = None,
) -> dict:
    """
    Выполнить skill по имени с precheck-цепочками.

    Args:
        skill_name: Имя skill (например "tariff.get_current")
        client: SberMobileClient с активной авторизацией
        params: Параметры от LLM
        confirm_fn: Callback для подтверждения write-операций.
        context: SkillContext для отслеживания состояния разговора.

    Returns:
        dict: {success, data, precheck_data?} или {success: False, error}
    """
    skill = SKILLS_BY_NAME.get(skill_name)
    if not skill:
        return {"error": f"Unknown skill: {skill_name}"}

    if context is None:
        context = SkillContext()

    precheck_data = None

    try:
        # ── Precheck chain ──
        chain = PRECHECK_CHAINS.get(skill_name)
        if chain:
            precheck_data = _run_precheck(chain, client, params)

        # ── Confirmation gate для write-операций ──
        if skill.requires_confirmation:
            if confirm_fn is None:
                return {
                    "success": False,
                    "needs_confirmation": True,
                    "skill": skill_name,
                    "description": skill.description[:200],
                    "precheck_data": precheck_data,
                    "error": "Write-операция требует подтверждения абонента",
                }
            if not confirm_fn(skill_name, skill.description[:200], precheck_data):
                return {
                    "success": False,
                    "error": "Абонент отказался от выполнения операции",
                }

        # ── Execute ──
        result = skill.execute(client, params)
        response = {"success": True, "data": result}
        if precheck_data is not None:
            response["precheck_data"] = precheck_data
        return response

    except Exception as e:
        return {"success": False, "error": str(e)}


def _run_precheck(chain: dict, client, params: dict):
    """Запустить precheck skill из цепочки."""
    precheck_name = chain["precheck"]
    precheck_skill = SKILLS_BY_NAME.get(precheck_name)
    if not precheck_skill:
        return None

    precheck_params = {
        target_key: params[source_key]
        for target_key, source_key in chain["param_map"].items()
        if source_key in params
    }

    try:
        return precheck_skill.execute(client, precheck_params)
    except Exception:
        return None


# ── Info ────────────────────────────────────────────────────

def print_skills_summary():
    """Вывести сводку всех skills."""
    domains = {}
    for s in ALL_SKILLS:
        domain = s.name.split(".")[0]
        domains.setdefault(domain, []).append(s)

    print(f"Skills total: {len(ALL_SKILLS)} "
          f"(read: {len(READ_ONLY)}, write: {len(CONFIRMATION_REQUIRED)})\n")

    for domain, skills in domains.items():
        print(f"  {domain}/ ({len(skills)} skills)")
        for s in skills:
            flag = " ⚡" if s.requires_confirmation else ""
            print(f"    {s.name}{flag}")
            print(f"      {s.description[:80]}...")
        print()
