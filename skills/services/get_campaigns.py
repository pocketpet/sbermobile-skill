"""
Skill: services.get_campaigns
Промо-кампании и персональные предложения.
"""

from skills.base import Skill


class GetCampaigns(Skill):
    name = "services.get_campaigns"

    description = (
        "Получить промо-кампании и персональные предложения абонента СберМобайл. "
        "Используй когда абонент спрашивает 'есть ли акции', "
        "'персональные предложения', 'промо-коды'."
    )

    input_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    requires_confirmation = False

    examples = [
        "Есть ли какие-то акции?",
        "Персональные предложения",
    ]

    api_endpoints = [
        "GET /v2/api/campaign-service/campaign/content/v2",
    ]

    def execute(self, client, params: dict) -> dict:
        return client.get_campaign_content()
