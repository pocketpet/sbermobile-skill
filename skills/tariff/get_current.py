"""
Skill: tariff.get_current
Текущий тариф абонента + доступные для перехода.
"""

from skills.base import Skill


class GetCurrentTariff(Skill):
    name = "tariff.get_current"

    description = (
        "Получить информацию о текущем тарифе абонента СберМобайл: название, "
        "абонентская плата, включённые пакеты (ГБ, минуты, SMS), доступные "
        "тарифы для перехода. Используй когда абонент спрашивает "
        "'какой у меня тариф', 'сколько я плачу', 'что входит в мой тариф'."
    )

    input_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    requires_confirmation = False

    examples = [
        "Какой у меня тариф?",
        "Сколько стоит мой тариф?",
        "Что входит в мой тариф?",
    ]

    api_endpoints = [
        "GET /v2/api/tariff-service/tariff/v2/connected-available",
    ]

    def execute(self, client, params: dict) -> dict:
        return client.get_tariff_connected_available()
