"""
Skill: account.get_profile
Профиль и персональные данные абонента.
"""

from skills.base import Skill


class GetProfile(Skill):
    name = "account.get_profile"

    description = (
        "Получить профиль абонента СберМобайл: персональные данные, "
        "информацию о контракте, привязанные карты. "
        "Используй когда абонент спрашивает 'мой профиль', "
        "'какой у меня номер', 'информация об абоненте'."
    )

    input_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    requires_confirmation = False

    examples = [
        "Мой профиль",
        "Какой у меня номер?",
        "Информация об абоненте",
    ]

    api_endpoints = [
        "GET /v2/api/client-service/customer-profile",
        "GET /v2/api/client-service/personal-info",
        "GET /v2/api/user-detail-service/elk/userinfo",
    ]

    def execute(self, client, params: dict) -> dict:
        profile = client.get_customer_profile()
        try:
            personal = client.get_personal_info()
        except Exception:
            personal = None
        try:
            userinfo = client.get_userinfo()
        except Exception:
            userinfo = None
        result = {"profile": profile}
        if personal:
            result["personal_info"] = personal
        if userinfo:
            result["userinfo"] = userinfo
        return result
