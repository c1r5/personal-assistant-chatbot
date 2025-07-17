from collections.abc import Awaitable
import logging
from typing import Any, Callable, Union

from aiogram import Bot

from constants import OWNER_USER_ID
from modules.bot.telegram.models.chat_message import BotMessage, UserMessage

logger = logging.getLogger(__name__)

UserMessageListener = Callable[[UserMessage], Union[Awaitable[Any], Any]]

class Chat:
    __user_message_listeners: list[UserMessageListener] = []

    def __init__(self, bot: Bot):
        self.bot = bot

    def add_user_message_listener(self, listener: UserMessageListener):
        self.__user_message_listeners.append(listener)

    def remove_user_message_listener(self, listener: UserMessageListener):
        self.__user_message_listeners.remove(listener)

    async def on_bot_message(self, message: UserMessage | None):
        if message is not None:
            await self.__notify_listeners(message)

    async def send_message(self, bot_message: BotMessage):
        try:
            await self.bot.send_message(
                    chat_id=OWNER_USER_ID,
                    text=bot_message.message,
                    reply_to_message_id=bot_message.reply_to_message_id if bot_message.reply_to_message_id else None,
                )
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def __notify_listeners(self, message: UserMessage):
        for listener in self.__user_message_listeners:
            await listener(message)
