from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile, Message
from aiogram.filters import Command

from typing import Callable, Awaitable, Optional
from uuid import uuid4
from io import BytesIO

from modules.chatbots.types.chatbot_connector import ChatbotConnector

OnMessageCallback = Callable[[Optional[str], str], Awaitable[None]]

class TelegramChatbotConnector(ChatbotConnector):
    def __init__(self,
        token: str,
        on_message: Optional[OnMessageCallback] = None
    ):
        self.__bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.__dp = Dispatcher()

        self.__on_message = on_message

        # Setup handlers manually
        self.__dp.message.register(self.__handle_health, Command("health"))
        self.__dp.message.register(self.__handle_version, Command("version"))
        self.__dp.message.register(self.__handle_message)

    async def start_listening(self):
        try:
            await self.__dp.start_polling(self.__bot)
        except Exception as e:
            print(f"Error starting Telegram bot: {e}")

    async def stop_listening(self):
        await self.__dp.stop_polling()

    async def send_message(self, text: str, chat_id: str):
        await self.__bot.send_message(chat_id=chat_id, text=text)

    async def send_document(self, chat_id: str, buffer: BytesIO, filename: Optional[str] = None):
        buffer.seek(0)
        input_file = BufferedInputFile(buffer.read(), filename=filename if filename is not None else str(uuid4()))
        await self.__bot.send_document(chat_id=chat_id, document=input_file)

    async def __handle_health(self, message: Message):
        await message.reply("Bot is running smoothly!")

    async def __handle_version(self, message: Message):
        await message.reply("1.0.0")

    async def __handle_message(self, message: Message):
        if self.__on_message:
            if message.text is not None and message.from_user is not None:
                await self.__on_message(message.text, str(message.from_user.id))
        else:
            await message.reply("Mensagem recebida!")
