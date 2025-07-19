from abc import ABC, abstractmethod
from io import BytesIO
from typing import Optional

class ChatbotConnector(ABC):
    @abstractmethod
    async def start_listening(self):
        pass

    @abstractmethod
    async def stop_listening(self):
        pass

    @abstractmethod
    async def send_message(self, text: str, chat_id: str):
        pass

    @abstractmethod
    async def send_document(self, chat_id: str, buffer: BytesIO, filename: Optional[str] = None):
        pass
