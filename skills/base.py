"""
Базовый класс для всех skills.
"""

from abc import ABC, abstractmethod


class Skill(ABC):
    """
    Базовый skill — атомарная способность AI-агента.

    Подклассы задают атрибуты как class-level поля:
        name:                   Уникальное имя (domain.action, например "tariff.get_current")
        description:            Описание для LLM — когда и зачем использовать этот skill
        input_schema:           JSON Schema параметров (для tool_use)
        requires_confirmation:  Нужно ли подтверждение абонента перед выполнением
        examples:               Примеры фраз абонента, при которых нужен этот skill
        api_endpoints:          Список API-эндпоинтов которые вызывает skill
    """

    name: str = ""
    description: str = ""
    input_schema: dict = {"type": "object", "properties": {}, "required": []}
    requires_confirmation: bool = False
    examples: list = []
    api_endpoints: list = []

    @abstractmethod
    def execute(self, client, params: dict) -> dict:
        """
        Выполнить skill.

        Args:
            client: SberMobileClient с активной авторизацией
            params: Параметры от LLM (согласно input_schema)

        Returns:
            dict с результатом для передачи обратно в LLM
        """
        ...

    def to_anthropic_tool(self) -> dict:
        """Формат Anthropic Tool Use."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

    def to_openai_tool(self) -> dict:
        """Формат OpenAI Function Calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }
