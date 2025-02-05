from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLM(ABC):
    @abstractmethod
    async def generate_course_outline(self, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def generate_lesson_detail(self, topic: str, content: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def chat(self, message: str) -> str:
        pass 