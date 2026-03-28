"""
Skill: tariff.list_available
Витрина тарифов и пакеты услуг.
"""

from skills.base import Skill


class ListAvailableTariffs(Skill):
    name = "tariff.list_available"

    description = (
        "Получить витрину тарифов СберМобайл и пакеты услуг. "
        "Показывает тарифы для самостоятельной регистрации и пакеты. "
        "Используй когда абонент хочет сменить тариф или узнать "
        "'какие тарифы есть', 'что дешевле', 'хочу другой тариф'."
    )

    input_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    requires_confirmation = False

    examples = [
        "Какие тарифы есть?",
        "Хочу сменить тариф",
        "Покажи тарифы подешевле",
    ]

    api_endpoints = [
        "GET /v2/api/tariff-service/selfreg/showcase",
        "GET /v2/api/tariff-service/service-package/",
    ]

    def execute(self, client, params: dict) -> dict:
        showcase = client.get_selfreg_showcase()
        try:
            packages = client.get_service_packages()
        except Exception:
            packages = None
        result = {"showcase": showcase}
        if packages:
            result["service_packages"] = packages
        return result
