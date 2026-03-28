"""
СберМобайл AI Agent — Demo с Anthropic Claude

Демонстрация полного цикла: пользователь общается с AI-агентом,
агент использует skills для работы с API СберМобайл.

Требования:
    pip install anthropic requests

    export ANTHROPIC_API_KEY=sk-ant-...
"""

import os
import json
import anthropic

from client import SberMobileClient
from skills import (
    get_tools_for_anthropic,
    execute_skill,
    SkillContext,
)


SYSTEM_PROMPT = """Ты — AI-ассистент СберМобайл. Помогаешь абонентам с вопросами о тарифах,
услугах, балансе и настройках. Ты дружелюбный, компетентный и проактивный.

Правила:
1. В начале разговора узнай что нужно абоненту.
2. Для любых действий с аккаунтом используй доступные tools (skills).
3. Write-операции требуют подтверждения — executor запросит его автоматически.
4. Отвечай на русском языке. Будь кратким но информативным.
5. Если данные не загрузились — не выдумывай, скажи что произошла ошибка.
6. Используй конкретные цифры (ГБ, минуты, рубли).
"""


def confirm_fn(skill_name: str, description: str, precheck_data=None) -> bool:
    """Запрашивает подтверждение у пользователя для write-операций."""
    print(f"\n⚠️  Агент хочет выполнить: {skill_name}")
    if precheck_data:
        print(f"   Предварительная проверка: {json.dumps(precheck_data, ensure_ascii=False, default=str)[:300]}")
    answer = input("   Подтвердить? (да/нет): ").strip().lower()
    return answer in ("да", "yes", "y", "д")


def run_agent():
    # ── Setup ───────────────────────────────────────────────
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Установи ANTHROPIC_API_KEY: export ANTHROPIC_API_KEY=sk-ant-...")
        return

    client = anthropic.Anthropic(api_key=api_key)
    sbermobile = SberMobileClient()
    tools = get_tools_for_anthropic()
    skill_context = SkillContext()

    # ── Auth ────────────────────────────────────────────────
    print("=== СберМобайл AI Agent Demo ===\n")

    if sbermobile.is_authenticated():
        print(f"Загружен токен для номера {sbermobile.phone}")
    else:
        phone = input("Номер телефона (+79XXXXXXXXX): ").strip()
        result = sbermobile.request_otp(phone)
        print(f"SMS отправлен: {result.get('statusInfo', {}).get('statusCode')}")

        otp = input("Код из SMS: ").strip()
        result = sbermobile.submit_otp(phone, otp)
        if not sbermobile.is_authenticated():
            print(f"Ошибка авторизации: {result}")
            return

    print("\nАвторизация успешна! Начинай общение (Ctrl+C для выхода)\n")
    print("-" * 60)

    # ── Chat loop ───────────────────────────────────────────
    messages = []

    while True:
        try:
            user_input = input("\nВы: ").strip()
            if not user_input:
                continue
        except (KeyboardInterrupt, EOFError):
            print("\n\nДо свидания!")
            break

        messages.append({"role": "user", "content": user_input})

        # Agentic loop — продолжаем пока LLM вызывает tools
        while True:
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",  # или другая модель Claude
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=messages,
            )

            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})

            tool_uses = [b for b in assistant_content if b.type == "tool_use"]

            if not tool_uses:
                for block in assistant_content:
                    if hasattr(block, "text"):
                        print(f"\nАгент: {block.text}")
                break

            # Выполняем tool calls через smart executor
            tool_results = []
            for tool_use in tool_uses:
                skill_name = tool_use.name
                params = tool_use.input

                print(f"  [skill: {skill_name}]")
                result = execute_skill(
                    skill_name,
                    sbermobile,
                    params,
                    confirm_fn=confirm_fn,
                    context=skill_context,
                )
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                })

            messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    run_agent()
