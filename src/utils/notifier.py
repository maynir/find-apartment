import asyncio
import os
import platform
from io import BytesIO

import requests
from telegram import Bot, InputMediaPhoto
from telegram.request import HTTPXRequest

from etc import config


class Notifier:
    def __init__(self, telegram_chat_id):
        request = HTTPXRequest(
            connect_timeout=10.0,
            read_timeout=120.0,
            write_timeout=120.0,
            pool_timeout=10.0,
        )
        self.telegram_bot = Bot(
            token=config.TELEGRAM_BOT_TOKEN,
            request=request
        )
        self.telegram_chat_id = telegram_chat_id

    async def send_telegram_message(self, message, images):
        async with self.telegram_bot:
            await self.telegram_bot.send_message(
                text=message, chat_id=self.telegram_chat_id
            )
            if images:
                await self.telegram_bot.send_media_group(
                    chat_id=self.telegram_chat_id, media=images
                )

            print(f"✉️ Telegram message sent")

    def notify(self, body, imgs_src=[], map=None):
        images = self.get_images(imgs_src)
        if map:
            images.append(InputMediaPhoto(map))
        asyncio.run(self.send_telegram_message(body, images))
        self.play_sound()

    def get_images(self, image_urls):
        media_group = []
        for url in image_urls:
            try:
                response = requests.get(url, timeout=10)
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Failed to download image {url}")
                continue
            if response.status_code == 200:
                image_data = BytesIO(response.content)  # Store image in memory
                media_group.append(InputMediaPhoto(image_data))
            else:
                print(f"⚠️ Failed to download image {url}: Status code {response.status_code}")
        return media_group

    def play_sound(self):
        """Plays a notification sound based on the OS"""
        try:
            if platform.system() == "Windows":
                import winsound

                winsound.MessageBeep()  # Default Windows beep sound
            elif platform.system() == "Darwin":  # macOS
                os.system(
                    "afplay /System/Library/Sounds/Glass.aiff"
                )  # Play built-in macOS sound
            else:  # Linux
                os.system(
                    "paplay /usr/share/sounds/freedesktop/stereo/message.oga"
                )  # Common Linux sound
        except Exception as e:
            print(f"⚠️ Failed to play sound: {e}")
