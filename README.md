# sbermobile-skill

Python-клиент и набор AI-skills для личного кабинета СберМобайл. Прямые REST API вызовы — без браузера, без Puppeteer.

> **Disclaimer**: Проект не аффилирован с ПАО Сбербанк или СберМобайл. Это неофициальный клиент, созданный в образовательных целях. API не является публичным и может измениться без предупреждения. Используйте на свой страх и риск.

## Зачем

У СберМобайл нет публичного API. Этот проект позволяет программно получать данные из личного кабинета (`lk.sbermobile.ru`) — точно так же, как это делает веб-интерфейс. Авторизация через SMS-код.

Два сценария использования:

1. **Python-клиент** — импортируешь `SberMobileClient`, вызываешь методы, получаешь JSON
2. **AI-skills для Claude Code** — 7 готовых skills, которые Claude может вызывать как tools

## Установка

```bash
git clone https://github.com/pocketpet/sbermobile-skill.git
cd sbermobile-skill
pip install -r requirements.txt
```

Зависимость одна — `requests`.

## Быстрый старт

```python
import sys; sys.path.insert(0, "/path/to/sbermobile-skill")
from client import SberMobileClient

c = SberMobileClient()

# Первый раз — авторизация по SMS
c.request_otp('+79XXXXXXXXX')
c.submit_otp('+79XXXXXXXXX', '123456')  # код из SMS

# Токен сохранится в /tmp/sbermobile_token.json
# При следующем запуске подхватится автоматически
```

## Что можно получить

```python
# Тариф и остатки (ГБ, минуты, SMS)
c.get_tariff_data(c.phone)

# Текущий тариф + доступные для перехода
c.get_tariff_connected_available()

# Подключённые услуги с ценами
c.get_options_connected(c.phone)

# Доступные опции для подключения
c.get_options()

# Рекомендуемая сумма пополнения
c.get_recommended_amount()

# Бонусы СберСпасибо
c.get_loyalty_state()

# Профиль абонента (ФИО, SIM-тип, статус)
c.get_customer_profile()

# Промо-акции и персональные предложения
c.get_campaign_content()

# Витрина тарифов
c.get_selfreg_showcase()
```

Все суммы возвращаются в копейках (39000 = 390 руб).

## AI Skills

7 read-only skills для использования с Claude или другими LLM:

| Skill | Описание |
|-------|----------|
| `account.get_balance` | Рекомендуемое пополнение, автоплатёж, бонусы СберСпасибо |
| `account.get_remainders` | Остатки пакетов: ГБ, минуты, SMS |
| `account.get_profile` | Профиль абонента, персональные данные |
| `tariff.get_current` | Текущий тариф + доступные для перехода |
| `tariff.list_available` | Витрина тарифов, пакеты услуг |
| `services.list_current` | Подключённые опции и услуги |
| `services.get_campaigns` | Промо-кампании, персональные предложения |

### Пример с Claude (agent_demo.py)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python examples/agent_demo.py
```

Запускается интерактивный чат, где Claude использует skills для ответов на вопросы об аккаунте.

## Структура проекта

```
sbermobile-skill/
├── client/
│   ├── __init__.py
│   └── sbermobile_client.py    # REST-клиент (read-only)
├── skills/
│   ├── base.py                 # Базовый класс Skill
│   ├── account/                # get_balance, get_remainders, get_profile
│   ├── tariff/                 # get_current, list_available
│   └── services/               # list_current, get_campaigns
├── examples/
│   └── agent_demo.py           # Интерактивный AI-агент на Claude
├── docs/
│   └── api-reference.md        # Документация всех эндпоинтов
├── requirements.txt
├── LICENSE
└── README.md
```

## Особенности API

Несколько неочевидных моментов, которые стоит знать:

- **Auth header** — `token: {value}`, а не `Authorization: Bearer`
- **Телефон** — 10 цифр без `+7`, поле называется `number`, не `phone`
- **Суммы** — в копейках, делить на 100
- **Read-only** — клиент содержит только GET-методы, никаких write-операций

Подробнее — в [docs/api-reference.md](docs/api-reference.md).

## Лицензия

[MIT](LICENSE)
