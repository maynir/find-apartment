import asyncio

from telegram import Bot

from src.etc import config


async def main():

    # Create bot object
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)

    # Get updates
    updates = await bot.get_updates()

    if not updates:
        print("No updates found")
    else:
        for update in updates:
            if update.message:

                # Show all message data if needed
                # print(update.message)

                # Show only chat id, title and message
                chat_id = update.message.chat.id
                chat_title = update.message.chat.title
                message_text = update.message.text
                print(
                    f"Chat ID: {chat_id}  | Chat Title: {chat_title} | Message: {message_text}"
                )


asyncio.run(main())
