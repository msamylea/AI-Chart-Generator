from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    async def get_response(self, prompt: str, model: str, temperature: float, max_tokens: int) -> str:
        pass