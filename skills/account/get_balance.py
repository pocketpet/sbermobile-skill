"""
Skill: account.get_balance
Финансовая информация: рекомендуемое пополнение, автоплатёж, бонусы.
"""

from skills.base import Skill


class GetBalance(Skill):
    name = "account.get_balance"

    description = (
        "Получить финансовую информацию абонента СберМобайл: "
        "рекомендуемая сумма пополнения, настройки автоплатежа, "
        "бонусы СберСпасибо. Используй когда абонент спрашивает "
        "'сколько пополнить', 'автоплатёж', 'бонусы', 'СберСпасибо'."
    )

    input_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    requires_confirmation = False

    examples = [
        "Сколько пополнить?",
        "Какой у меня автоплатёж?",
        "Сколько бонусов СберСпасибо?",
    ]

    api_endpoints = [
        "GET /v2/api/payment-service/payment/recommended_amount",
        "GET /v2/api/payment-service/loyalty/state",
    ]

    def execute(self, client, params: dict) -> dict:
        result = {}
        result["recommended_amount"] = client.get_recommended_amount()
        try:
            result["loyalty"] = client.get_loyalty_state()
        except Exception:
            pass
        return result
