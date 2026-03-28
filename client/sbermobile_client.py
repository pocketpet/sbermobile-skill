"""
СберМобайл API Client — клиент для личного кабинета.

Обёртка над REST API lk.sbermobile.ru/v2/api/ с поддержкой
авторизации через phone + SMS OTP (gateway).
"""

import os
import re
import json
import requests


BASE_URL = "https://lk.sbermobile.ru/v2/api"

# При необходимости обновите User-Agent и X-User-info
# на актуальные значения из lk.sbermobile.ru
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Origin": "https://lk.sbermobile.ru",
    "Referer": "https://lk.sbermobile.ru/",
    "X-User-info": "SBTMA/2.3 desktop/Mac OS X/PWA (desktop)",
}

TIMEOUTS = {
    "default": 15,
    "auth": 30,
}

TOKEN_FILE = os.path.expanduser("/tmp/sbermobile_token.json")


class SberMobileAuthError(Exception):
    """Ошибка авторизации."""
    pass


class SberMobileAPIError(Exception):
    """Ошибка API."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class SberMobileClient:
    def __init__(self, auto_load_token: bool = True):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.token = None
        self.phone = None
        self._otp_summary = None
        if auto_load_token:
            self.load_token()

    # ── Helpers ─────────────────────────────────────────────

    def _url(self, path: str) -> str:
        if path.startswith("http"):
            return path
        return f"{BASE_URL}{path}"

    def _check_response(self, r: requests.Response) -> dict:
        """Проверить ответ и вернуть JSON."""
        if r.status_code == 401:
            raise SberMobileAuthError(
                r.json().get("statusInfo", {}).get("statusMessage", "Unauthorized")
                if "json" in r.headers.get("content-type", "") else "Unauthorized (401)"
            )
        if r.status_code == 403:
            raise SberMobileAuthError("Forbidden (403)")
        try:
            data = r.json()
        except ValueError:
            return {"_raw": r.text[:2000], "_status": r.status_code}
        if isinstance(data, dict):
            status_info = data.get("statusInfo", {})
            if status_info.get("statusCode") and status_info["statusCode"] != "OK":
                raise SberMobileAPIError(
                    status_info["statusCode"],
                    status_info.get("statusMessage", "Unknown error"),
                )
        return data

    def _auth_headers(self) -> dict:
        """Заголовки с токеном авторизации."""
        if self.token:
            return {"token": self.token}
        return {}

    def _get(self, path: str, params=None, timeout=None) -> dict:
        r = self.session.get(
            self._url(path),
            params=params,
            headers=self._auth_headers(),
            timeout=timeout or TIMEOUTS["default"],
        )
        return self._check_response(r)

    def _post(self, path: str, json_body=None, form_data=None, timeout=None) -> dict:
        kwargs = {
            "timeout": timeout or TIMEOUTS["default"],
            "headers": self._auth_headers(),
        }
        if json_body is not None:
            kwargs["json"] = json_body
        elif form_data is not None:
            kwargs["data"] = form_data
            kwargs["headers"]["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        r = self.session.post(self._url(path), **kwargs)
        return self._check_response(r)

    # ── Auth (gateway) ──────────────────────────────────────

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Нормализовать телефон в 10-значный формат (без +7/8/7)."""
        digits = re.sub(r"[^\d]", "", phone)
        if len(digits) == 11 and digits[0] in ("7", "8"):
            return digits[1:]
        if len(digits) == 10:
            return digits
        return digits

    def request_otp(self, phone: str, additional: bool = False) -> dict:
        """
        Запрос SMS-кода на номер.
        POST /v2/api/gateway/send_password
        Body: {"number": "9XXXXXXXXX", "additional": "false"}
        """
        number = self._normalize_phone(phone)
        self.phone = number
        data = self._post(
            "/gateway/send_password",
            json_body={
                "number": number,
                "additional": str(additional).lower(),
            },
            timeout=TIMEOUTS["auth"],
        )
        self._otp_summary = data.get("data", {}).get("summary")
        return data

    def submit_otp(self, phone: str, otp: str, device_id: str = None) -> dict:
        """
        Подтверждение SMS-кода, получение токена.
        POST /v2/api/gateway/login
        Body: {number, password, screen, appVersionName, appVersionCode,
               system, systemVersion, deviceId}
        """
        import uuid
        import platform

        number = self._normalize_phone(phone)
        data = self._post(
            "/gateway/login",
            json_body={
                "number": number,
                "password": otp,
                "screen": "1920x1080",
                "appVersionName": "2.3",
                "appVersionCode": "2.0.0",
                "system": "desktop",
                "systemVersion": platform.system() + " " + platform.release(),
                "deviceId": device_id or str(uuid.uuid4()),
            },
            timeout=TIMEOUTS["auth"],
        )
        # Извлечь токен из ответа
        token = (
            data.get("data", {}).get("token")
            or data.get("token")
            or data.get("jwtToken")
            or data.get("access_token")
        )
        if token:
            self.token = token
            self.save_token()
        return data

    def is_authenticated(self) -> bool:
        return self.token is not None

    def save_token(self):
        """Сохранить токен в файл для повторного использования."""
        if self.token:
            with open(TOKEN_FILE, "w") as f:
                json.dump({"token": self.token, "phone": self.phone}, f)

    def load_token(self) -> bool:
        """Загрузить токен из файла. Возвращает True если загружен."""
        try:
            with open(TOKEN_FILE) as f:
                data = json.load(f)
            self.token = data.get("token")
            self.phone = data.get("phone")
            return self.token is not None
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return False

    # ── Tariff Service ──────────────────────────────────────

    def get_tariff_connected_available(self, additional_number: str = "") -> dict:
        """Текущий тариф + доступные для перехода."""
        return self._get(
            "/tariff-service/tariff/v2/connected-available",
            {"additionalNumber": additional_number},
        )

    def get_tariff_data(self, numbers: str) -> dict:
        """Данные тарифа по номерам (запятая-разделённые)."""
        return self._get("/tariff-service/tariff/data", {"numbers": numbers})

    def get_tariff_option_status(self) -> dict:
        """Статус тарифной опции."""
        return self._get("/tariff-service/tariff/option/status")

    def get_service_packages(self) -> dict:
        """Пакеты услуг."""
        return self._get("/tariff-service/service-package/")

    def get_selfreg_showcase(self) -> dict:
        """Витрина тарифов для самостоятельной регистрации."""
        return self._get("/tariff-service/selfreg/showcase")

    def get_prime_profile(self) -> dict:
        """Профиль СберПрайм."""
        return self._get("/tariff-service/prime/profile/v2")

    # ── Options (Services) ──────────────────────────────────

    def get_options(self, additional_number: str = "") -> dict:
        """Доступные опции/услуги."""
        return self._get(
            "/tariff-service/v2/options",
            {"additionalNumber": additional_number},
        )

    def get_options_connected(self, numbers: str) -> dict:
        """Подключённые опции по номерам."""
        return self._get(
            "/tariff-service/v2/options/connected",
            {"numbers": numbers},
        )

    # ── Secure Account ──────────────────────────────────────

    def get_secure_account(self, additional_number: str = "") -> dict:
        """Информация о защите аккаунта (ассистент)."""
        return self._get(
            "/tariff-service/v1/secure-account/assistant",
            {"additionalNumber": additional_number},
        )

    def get_secure_info(self, additional_number: str = "") -> dict:
        """Расширенная информация о безопасности."""
        return self._get(
            "/tariff-service/v2/secure-account/secure-info",
            {"additionalNumber": additional_number},
        )

    def get_secure_banner(self, numbers: str) -> dict:
        """Баннер безопасности."""
        return self._get(
            "/tariff-service/v2/secure-account/banner",
            {"numbers": numbers},
        )

    # ── Payment Service ─────────────────────────────────────

    def get_cards(self) -> dict:
        """Привязанные банковские карты."""
        return self._get("/payment-service/card")

    def get_loyalty_state(self) -> dict:
        """Состояние программы лояльности."""
        return self._get("/payment-service/loyalty/state")

    def get_recommended_amount(self) -> dict:
        """Рекомендуемая сумма пополнения."""
        return self._get("/payment-service/payment/recommended_amount")

    def get_autopay(self) -> dict:
        """Настройки автоплатежа."""
        return self._get("/payment-service/v3/auto-pay")

    def get_autopay_services(self) -> dict:
        """Услуги автоплатежа."""
        return self._get("/payment-service/v3/auto-pay/services")

    # ── Campaign Service ────────────────────────────────────

    def get_campaign_content(self, additional_number: str = "") -> dict:
        """Промо-кампании и предложения."""
        return self._get(
            "/campaign-service/campaign/content/v2",
            {"additionalNumber": additional_number},
        )

    # ── Family (Friends & Family) ───────────────────────────

    def get_family_group(self, msisdns: list[str]) -> dict:
        """Информация о семейной группе."""
        return self._get(
            "/friends-and-family-service/v1/group",
            {"msisdn": ",".join(msisdns)},
        )

    def get_family_invitations_price(self) -> dict:
        """Стоимость приглашений в семью."""
        return self._get("/friends-and-family-service/v1/invitations/price")

    # ── User Detail Service ─────────────────────────────────

    def get_sber_sdk_params(self) -> dict:
        """Параметры SberID SDK."""
        return self._get("/user-detail-service/sber/sdk/params")

    def get_stories(self, numbers: str) -> dict:
        """Сторис для номеров."""
        return self._get(
            "/user-detail-service/stories",
            {"numbers": numbers},
        )

    # ── Feedback Service ────────────────────────────────────

    def get_faq_buttons(self) -> dict:
        """Кнопки FAQ."""
        return self._get("/feedback-service/faq-buttons")

    def get_tickets(self, numbers: str) -> dict:
        """Обращения в поддержку."""
        return self._get("/feedback-service/tickets", {"numbers": numbers})

    # ── Secure Account (расширенное) ─────────────────────────

    def get_assistant_mode(self) -> dict:
        """Режим ассистента (Хранитель)."""
        return self._get("/tariff-service/v1/secure-account/assistant/mode")

    def get_assistant_personages(self) -> dict:
        """Персонажи ассистента."""
        return self._get("/tariff-service/v1/secure-account/assistant/personages")

