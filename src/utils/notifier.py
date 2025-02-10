from telegram import Bot
import asyncio
from etc import config

class Notifier:
    def __init__(self):
        self.telegram_bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        self.telegram_chat_id = config.CHAT_ID

    async def send_telegram_message(self, message):
        async with self.telegram_bot:
            await self.telegram_bot.send_message(
                text=message, chat_id=self.telegram_chat_id
            )
            print(f"✉️ Telegram message sent")

    def notify(self, body):
        asyncio.run(self.send_telegram_message(body))
