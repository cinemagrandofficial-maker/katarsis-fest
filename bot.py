import os
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="ОТКРЫТЬ КАТАРСИС FEST",
                    web_app=WebAppInfo(
                        url="https://cinemagrandofficial-maker.github.io/katarsis-fest/?v=3"
                    )
                )
            ]
        ]
    )

    await message.answer(
        "🎭 КАТАРСИС fest.\n\n"
        "26 сентября · Москва · Поляна\n\n"
        "Музыка. Стиль. Искусство.\n\n"
        "Открывай фестиваль:",
        reply_markup=keyboard
    )


async def main():
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
