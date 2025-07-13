from collections.abc import Awaitable
import logging
from typing import Any, Callable, Union

from aiogram import Bot

from modules.bot.telegram.constants import OWNER_USER_ID
from modules.bot.telegram.models.chat_message import BotMessage, UserMessage

logger = logging.getLogger(__name__)

MessageCallback = Callable[[UserMessage], Union[Awaitable[Any], Any]]

class Chat:
    __message_listeners: list[MessageCallback] = []

    def __init__(self, bot: Bot):
        self.bot = bot

    def add_on_message_listener(self, cb: MessageCallback):
        self.__message_listeners.append(cb)
        return self

    def remove_on_message_listener(self, cb: MessageCallback):
        self.__message_listeners.remove(cb)
        return self

    async def emit_message(self, message: UserMessage | None):
        if message is not None:
            logger.info(f"Chat message: {message}")
            for listener in self.__message_listeners:
                await listener(message)

    async def send_message(self, bot_message: BotMessage):
        try:
            await self.bot.send_message(
                    chat_id=OWNER_USER_ID,
                    text=bot_message.message,
                    reply_to_message_id=bot_message.reply_to_message_id if bot_message.reply_to_message_id else None,
                )
        except Exception as e:
            logger.error(f"Error sending message: {e}")
