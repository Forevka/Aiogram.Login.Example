import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.login_url import LoginUrl

from config import BOT_TOKEN, HOST_URL

dp = Dispatcher()

logger = logging.getLogger(__name__)


@dp.message(commands={"login"})
async def cmd_login(message: Message) -> None:
    login_markup = InlineKeyboardMarkup(**{
        "inline_keyboard": [
            [
                InlineKeyboardButton(**{
                    "login_url": LoginUrl(**{
                        "url": f"{HOST_URL}/auth",
                    }),
                    "text": "login",
                })
            ]
        ]
    })

    await message.answer("Here login button", reply_markup=login_markup)


def main() -> None:
    bot = Bot(BOT_TOKEN, parse_mode="HTML")

    dp.run_polling(bot)


if __name__ == "__main__":
    main()
