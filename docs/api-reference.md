# СберМобайл API Reference

## Архитектура

- **SPA**: `https://lk.sbermobile.ru/`
- **API Base**: `https://lk.sbermobile.ru/v2/api/`
- **Auth**: Phone + SMS OTP через gateway
- **Token header**: `token: {value}` (НЕ `Authorization: Bearer`!)

## Auth Flow

```
1. POST /v2/api/gateway/send_password
   Body: {"number": "9XXXXXXXXX", "additional": "false"}
   Headers: X-User-info: SBTMA/2.3 desktop/Mac OS X/PWA (desktop)
   → Отправляет SMS с паролем
   → Response: {statusInfo: {statusCode: "OK"}, data: {summary: "..."}}

2. POST /v2/api/gateway/login
   Body: {"number": "9XXXXXXXXX", "password": "XXXX",
          "screen": "1920x1080", "appVersionName": "2.3",
          "appVersionCode": "2.0.0", "system": "desktop",
          "systemVersion": "...", "deviceId": "uuid-v4"}
   → Возвращает token

3. Все запросы:  Header "token: {value}"  +  "X-User-info: SBTMA/2.3 desktop/Mac OS X/PWA (desktop)"
```

**ВАЖНО**: Поле `number` — 10 цифр без +7 (например `9XXXXXXXXX`), НЕ `phone`.

## Эндпоинты

### client-service — Профиль
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/client-service/customer-profile` | Профиль абонента |
| GET | `/client-service/customer-profile?additionalNumber={n}` | Профиль доп. номера |
| GET | `/client-service/personal-info` | Персональные данные |
| GET | `/client-service/contract` | Данные контракта |

### tariff-service — Тарифы и опции
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/tariff-service/tariff/v2/connected-available?additionalNumber=` | Текущий тариф + доступные |
| GET | `/tariff-service/tariff/data?numbers={n1,n2}` | Данные тарифа по номерам |
| GET | `/tariff-service/tariff/option/status` | Статус тарифной опции |
| GET | `/tariff-service/service-package/` | Пакеты услуг |
| GET | `/tariff-service/selfreg/showcase` | Витрина тарифов |
| GET | `/tariff-service/prime/profile/v2` | Профиль СберПрайм |
| GET | `/tariff-service/v2/options?additionalNumber=` | Доступные опции |
| GET | `/tariff-service/v2/options/connected?numbers=` | Подключённые опции |

### Secure Account (защита)
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/tariff-service/v1/secure-account/assistant?additionalNumber=` | Ассистент |
| GET | `/tariff-service/v1/secure-account/assistant/mode` | Режим ассистента |
| GET | `/tariff-service/v1/secure-account/assistant/personages` | Персонажи |
| POST | `/tariff-service/v1/secure-account/assistant/whitelist/add` | Добавить в белый список |
| POST | `/tariff-service/v1/secure-account/assistant/whitelist/remove` | Удалить из белого списка |
| GET | `/tariff-service/v2/secure-account/banner?numbers=` | Баннер безопасности |
| GET | `/tariff-service/v2/secure-account/secure-info?additionalNumber=` | Инфо о безопасности |

### payment-service — Платежи
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/payment-service/card` | Привязанные карты |
| GET | `/payment-service/loyalty/state` | Лояльность |
| GET | `/payment-service/payment/recommended_amount` | Рекомендуемая сумма |
| POST | `/payment-service/payment/v2` | Оплата |
| POST | `/payment-service/prime/payment` | Оплата СберПрайм |
| GET | `/payment-service/v3/auto-pay` | Автоплатёж |
| GET | `/payment-service/v3/auto-pay/services` | Услуги автоплатежа |
| GET | `/payment-service/v3/auto-pay/date` | Дата автоплатежа |
| GET | `/payment-service/v3/auto-pay/threshold` | Порог автоплатежа |

### campaign-service — Кампании/промо
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/campaign-service/campaign/content/v2?additionalNumber=` | Промо-контент |
| POST | `/campaign-service/campaign/callback` | Callback кампании |

### friends-and-family-service — Семья
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/friends-and-family-service/v1/group?msisdn={n1,n2}` | Семейная группа |
| GET | `/friends-and-family-service/v1/invitations/price` | Стоимость приглашений |
| POST | `/friends-and-family-service/v1/invitations` | Отправить приглашение |
| POST | `/friends-and-family-service/v1/group/delete_user` | Удалить из группы |
| POST | `/friends-and-family-service/v1/group/name` | Изменить имя группы |

### user-detail-service — Пользователь
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/user-detail-service/elk/userinfo` | Инфо пользователя (ЕЛК) |
| GET | `/user-detail-service/sber/sdk/params` | Параметры SberID SDK |
| POST | `/user-detail-service/sber/v2/auth/login` | Авторизация SberID |
| POST | `/user-detail-service/messenger/open_chat` | Открыть чат |
| GET | `/user-detail-service/stories?numbers={n1,n2}` | Сторис |

### feedback-service — Обратная связь
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/feedback-service/faq-buttons` | Кнопки FAQ |
| POST | `/feedback-service/rate` | Оценка |
| GET | `/feedback-service/tickets?numbers=` | Обращения |
| POST | `/feedback-service/adjustment/personal/v2` | Корректировка |

### number-transfer-service — MNP (перенос номера)
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/number-transfer-service/number/check` | Проверка номера |
| POST | `/number-transfer-service/number/confirm` | Подтверждение |

## Gateway (Auth)
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/gateway/send_password` | Отправить SMS с паролем |
| POST | `/gateway/login` | Авторизация (phone + password) |
| POST | `/gateway/additional_number` | Добавить доп. номер |

## Ошибки

Формат ошибок:
```json
{
  "statusInfo": {
    "statusMessage": "Ошибка авторизации. Пожалуйста, авторизуйтесь повторно.",
    "statusCode": "TOKEN_NOT_FOUND"
  },
  "time": "2026-01-01T00:00:00.000"
}
```

Известные коды:
- `TOKEN_NOT_FOUND` — нет токена авторизации (401)
- `MAINTENANCE_WORK` — технические работы
- `NOT_SAME_PERSON` — не тот пользователь
- `SERVICE_IS_UNAVAILABLE` — сервис недоступен

## Статус тестирования

### Протестировано (возвращают данные)
| Метод | Эндпоинт | Результат |
|-------|----------|-----------|
| POST | `/gateway/send_password` | OK — SMS отправляется |
| POST | `/gateway/login` | OK — токен получен |
| GET | `/client-service/customer-profile` | OK — ФИО, SIM, статус |
| GET | `/client-service/personal-info` | OK — паспорт, адрес, договор |
| GET | `/tariff-service/tariff/v2/connected-available` | OK — тариф + опции |
| GET | `/tariff-service/tariff/data` | OK — тариф, остатки, баланс |
| GET | `/tariff-service/v2/options/connected` | OK — подключённые услуги |
| GET | `/tariff-service/prime/profile/v2` | OK — статус СберПрайм |
| GET | `/payment-service/payment/recommended_amount` | OK — рекомендуемое пополнение |
| GET | `/payment-service/loyalty/state` | OK — бонусы СберСпасибо |
| GET | `/payment-service/card` | OK — привязанные карты |
| GET | `/payment-service/v3/auto-pay` | OK — автоплатёж (пустой) |
| GET | `/campaign-service/campaign/content/v2` | OK — промо-кампании |
| GET | `/user-detail-service/elk/userinfo` | OK (требует токен) |
| GET | `/user-detail-service/stories` | OK — сторис, MNP, ассистент |
| GET | `/feedback-service/tickets` | OK — пустой список |
| GET | `/friends-and-family-service/v1/group` | OK |

### Не протестировано (MAINTENANCE_WORK при попытке)
| Метод | Эндпоинт |
|-------|----------|
| GET | `/tariff-service/v1/secure-account/assistant` |
| GET | `/tariff-service/v1/secure-account/assistant/mode` |
| GET | `/tariff-service/v1/secure-account/assistant/personages` |
| GET | `/tariff-service/v2/secure-account/secure-info` |
| GET | `/tariff-service/v2/secure-account/banner` |
| GET | `/client-service/contract` |
| GET | `/feedback-service/faq-buttons` |
| GET | `/payment-service/v3/auto-pay/services` |
| GET | `/user-detail-service/sber/sdk/params` |
| GET | `/tariff-service/selfreg/showcase` |
| GET | `/tariff-service/service-package/` |

### Write-операции (эндпоинты найдены, НЕ тестировались)
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/payment-service/payment/v2` | Оплата связи |
| POST | `/payment-service/v3/auto-pay` | Настройка автоплатежа |
| POST | `/friends-and-family-service/v1/invitations` | Приглашение в семью |
| POST | `/friends-and-family-service/v1/group/name` | Переименовать группу |
| POST | `/friends-and-family-service/v1/group/delete_user` | Удалить из группы |
| POST | `/tariff-service/v1/secure-account/assistant/whitelist/add` | Белый список |
| POST | `/tariff-service/v1/secure-account/assistant/whitelist/remove` | Убрать из белого списка |
| POST | `/user-detail-service/messenger/open_chat` | Открыть чат поддержки |
| POST | `/feedback-service/rate` | Оценка |
| POST | `/feedback-service/adjustment/personal/v2` | Корректировка |
| POST | `/campaign-service/campaign/callback` | Активация промо |
| POST | `/number-transfer-service/number/check` | Проверка номера MNP |
| POST | `/number-transfer-service/number/confirm` | Подтверждение MNP |
| POST | `/payment-service/prime/payment` | Оплата СберПрайм |

## Зависимости
- Python 3.9+
- requests
