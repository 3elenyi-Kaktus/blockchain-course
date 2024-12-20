import asyncio
import logging
import os
from threading import Thread
from time import sleep

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InputFile, FSInputFile


from bet import Bet
from routers.bet_create import bet_create_router
from routers.empty_stub import empty_stub_router
from routers.bet_operations import bet_operations_router

dispatcher = Dispatcher()
dispatcher.include_routers(bet_create_router, bet_operations_router, empty_stub_router)




class TelegramBot:
    def __init__(self):
        self.token: str = "7360850640:AAGyrJaO5KgM6xOQF8-22J1C5I-AqKAlIjU"
        self.bot: Bot = Bot(token=self.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.users: list[str] = []

        # self.bets: list[Bet] = []

    async def run(self) -> None:
        await dispatcher.start_polling(self.bot)


telegram_bot: TelegramBot = TelegramBot()


@dispatcher.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dispatcher.message(Command("usage"))
async def usage(message: Message) -> None:
    await message.answer(f"Send money to {'addr'}.")

@dispatcher.message(Command("register"))
async def register(message: Message) -> None:
    user_id: int = message.from_user.id
    if user_id in telegram_bot.users:
        await message.answer(f"You are already registered, your id: \"{user_id}\".")
    telegram_bot.users += [user_id]
    await message.answer(f"Registered! Your id: \"{user_id}\".")

# @dispatcher.message(Command("list_bets"))
# async def list_bets(message: Message) -> None:
#     user_id: int = message.from_user.id
#     if user_id in telegram_bot.users:
#         await message.answer(f"You are already registered, your id: \"{user_id}\".")
#     telegram_bot.users += [user_id]
#     await message.answer(f"Registered! Your id: \"{user_id}\".")
#
# @dispatcher.message(Command("make_bet"))
# async def make_bet(message: Message) -> None:
#     user_id: int = message.from_user.id
#     if user_id in telegram_bot.users:
#         await message.answer(f"You are already registered, your id: \"{user_id}\".")
#     telegram_bot.users += [user_id]
#     await message.answer(f"Registered! Your id: \"{user_id}\".")


stop_requested: bool = False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(asyncio_loop)

    asyncio_loop.run_until_complete(telegram_bot.run())
    stop_requested = True
