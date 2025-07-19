from modules.chatbots.types.chatbot_connector import ChatbotConnector
import asyncio

class MessageDispatcher:
    def __init__(self):
        self.__connectors: dict[str, ChatbotConnector] = {}

    def add_connector(self, connector_id: str, connector: ChatbotConnector):
        self.__connectors[connector_id] = connector

    def start_listening(self) -> list[asyncio.Task]:
        tasks = []

        for connector in self.__connectors.values():
            task = asyncio.create_task(connector.start_listening())
            tasks.append(task)

        return tasks

    async def dispatch_message(self, message: str, chat_id: str):
        for connector in self.__connectors.values():
            await connector.send_message(message, chat_id)
