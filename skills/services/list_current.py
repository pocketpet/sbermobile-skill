"""
Skill: services.list_current
Подключённые опции и услуги.
"""

from skills.base import Skill


class ListCurrentServices(Skill):
    name = "services.list_current"

    description = (
        "Получить список подключённых услуг и опций абонента СберМобайл. "
        "Показывает активные платные и бесплатные опции, а также доступные. "
        "Используй когда абонент спрашивает 'какие услуги подключены', "
        "'за что я плачу', 'мои подписки', 'мои опции'."
    )

    input_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    requires_confirmation = False

    examples = [
        "Какие услуги подключены?",
        "За что я плачу помимо тарифа?",
        "Мои подписки",
        "Список услуг",
    ]

    api_endpoints = [
        "GET /v2/api/tariff-service/v2/options",
        "GET /v2/api/tariff-service/v2/options/connected",
    ]

    def execute(self, client, params: dict) -> dict:
        options = client.get_options()
        return options
