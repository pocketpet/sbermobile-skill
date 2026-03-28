---
name: sbermobile
description: >
  This skill should be used when the user asks to "check SberMobile balance",
  "view SberMobile tariff", "manage SberMobile services",
  "check remaining minutes/SMS/GB on SberMobile",
  or mentions СберМобайл, SberMobile, or mobile operator account.
version: 0.2.0
---

# СберМобайл — личный кабинет оператора

Проект: `sbermobile_skill/`
API документация: `docs/api-reference.md`

## Python client

```python
import sys; sys.path.insert(0, "/path/to/sbermobile_skill")
from client import SberMobileClient

c = SberMobileClient()  # загрузит токен из /tmp/sbermobile_token.json
```

### Если токен протух (TOKEN_NOT_FOUND):
```python
c.request_otp('+79XXXXXXXXX')
# Спросить SMS-код у пользователя
c.submit_otp('+79XXXXXXXXX', '<код>')
```

### Основные вызовы
```python
c.get_tariff_data('9XXXXXXXXX')       # Тариф + остатки (ГБ, мин, SMS)
c.get_tariff_connected_available()    # Текущий тариф + доступные опции
c.get_recommended_amount()            # Рекомендуемое пополнение
c.get_loyalty_state()                 # Бонусы СберСпасибо
c.get_options_connected('9XXXXXXXXX') # Подключённые услуги
c.get_campaign_content()              # Промо-акции
c.get_selfreg_showcase()              # Витрина тарифов
```

## Правила
- Суммы в копейках (39000 = 390 руб) — делить на 100 при показе
- Отвечай по-русски, кратко

$ARGUMENTS
