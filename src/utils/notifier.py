from telegram import Bot, InputMediaPhoto
import asyncio
from etc import config
import platform
import os
import requests
from io import BytesIO

class Notifier:
    def __init__(self):
        self.telegram_bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        self.telegram_chat_id = config.CHAT_ID

    async def send_telegram_message(self, message, images):
        async with self.telegram_bot:
            await self.telegram_bot.send_message(
                text=message, chat_id=self.telegram_chat_id
            )
            if images:
                await self.telegram_bot.send_media_group(chat_id=self.telegram_chat_id, media=images)

            print(f"✉️ Telegram message sent")

    def notify(self, body, imgs_src = []):
        images = self.get_images(imgs_src)
        asyncio.run(self.send_telegram_message(body, images))
        self.play_sound()

    def get_images(self, image_urls):
        media_group =[]
        for url in image_urls:
            response = requests.get(url)
            if response.status_code == 200:
                image_data = BytesIO(response.content)  # Store image in memory
                media_group.append(InputMediaPhoto(image_data))
        return media_group

    def play_sound(self):
        """Plays a notification sound based on the OS"""
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.MessageBeep()  # Default Windows beep sound
            elif platform.system() == "Darwin":  # macOS
                os.system("afplay /System/Library/Sounds/Glass.aiff")  # Play built-in macOS sound
            else:  # Linux
                os.system("paplay /usr/share/sounds/freedesktop/stereo/message.oga")  # Common Linux sound
        except Exception as e:
            print(f"⚠️ Failed to play sound: {e}")