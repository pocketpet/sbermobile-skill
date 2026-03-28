"""
Skill: account.get_remainders
Остатки пакетов: гигабайты, минуты, SMS.
"""

from skills.base import Skill


class GetRemainders(Skill):
    name = "account.get_remainders"

    description = (
        "Получить остатки пакетов абонента СберМобайл: гигабайты интернета, "
        "минуты звонков, SMS, подключённые допы. "
        "Используй когда абонент спрашивает 'сколько гигабайт "
        "осталось', 'хватит ли интернета', 'сколько минут осталось'."
    )

    input_schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    requires_confirmation = False

    examples = [
        "Сколько гигабайт осталось?",
        "Сколько минут у меня?",
        "Какие у меня остатки?",
    ]

    api_endpoints = [
        "GET /v2/api/tariff-service/tariff/data",
    ]

    def execute(self, client, params: dict) -> dict:
        return client.get_tariff_data(client.phone)
