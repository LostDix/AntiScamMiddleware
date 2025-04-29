import logging
from collections import defaultdict
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update, Message
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


WARNING_TEXT = """
⚠️ <b>Внимание! Участились случаи мошенничества!</b>

Дорогие пользователи, будьте бдительны! В последнее время участились попытки обмана.
🔹 Никогда не переводите средства незнакомым людям!
🔹 Администрация НЕ запрашивает переводы.
🔹 Проверяйте информацию и не доверяйте подозрительным предложениям.

Берегите себя и свои финансы!
"""

class AntiScamMiddleware(BaseMiddleware):
    def __init__(self, bot):
        self.bot = bot
        self.last_warning_time = {}  # {chat_id: last_warning_datetime}
        self.message_counters = defaultdict(int)  # {chat_id: message_count}
        super().__init__()
        logger.info("Initialized AntiScamMiddleware")

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        try:
            message = event.message or event.edited_message
            if not message:
                return await handler(event, data)

            # Проверяем тип чата - работаем только в группах/супергруппах
            if not self._is_valid_chat_type(message):
                return await handler(event, data)

            if self._is_service_message(message):
                return await handler(event, data)

            chat_id = message.chat.id

            # Обновляем счетчик сообщений
            self.message_counters[chat_id] += 1

            # Проверяем условия для общего чата
            if not message.reply_to_message and await self._check_general_warning(message):
                await self._send_warning(message)
                self.last_warning_time[chat_id] = datetime.now()
                self.message_counters[chat_id] = 0

            return await handler(event, data)

        except Exception as e:
            logger.exception(f"Error in AntiScamMiddleware: {e}")
            return await handler(event, data)

    def _is_valid_chat_type(self, message: Message) -> bool:
        """Проверяет, что сообщение пришло из нужного типа чата"""
        chat_type = message.chat.type
        # Работаем только в группах и супергруппах
        return chat_type in ["group", "supergroup"]

    async def _check_general_warning(self, message: Message) -> bool:
        """Проверяет условия для отправки предупреждения в общий чат"""
        chat_id = message.chat.id

        # Если не было предупреждений - отправляем
        if chat_id not in self.last_warning_time:
            return True

        # Проверяем временной интервал (3 часа)
        if (datetime.now() - self.last_warning_time[chat_id]) < timedelta(hours=3):
            return False

        # Проверяем количество сообщений (50+)
        return self.message_counters[chat_id] >= 50

    async def _send_warning(self, message: Message):
        """Отправляет предупреждение в общий чат"""
        try:
            await self.bot.send_message(
                chat_id=message.chat.id,
                text=WARNING_TEXT,
                parse_mode="HTML"
            )
            logger.info(f"Sent scam warning to chat {message.chat.id}")
        except Exception as e:
            logger.error(f"Failed to send warning message: {e}")

    def _is_service_message(self, message: Message) -> bool:
        """Проверяет служебные сообщения"""
        return (not message.from_user or
                message.from_user.id == 777000 or
                message.new_chat_members or
                message.left_chat_member or
                message.pinned_message)