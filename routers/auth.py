import json
import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from storage import storage
from user_states import UserState, set_user_state, get_user_state
from callbacks import Callback

auth_router = Router(name=__name__)
last_messages: dict[int, Message] = {}


def set_last_message(user_id: int, message: Message):
    last_messages[user_id] = message


def clear_last_message(user_id: int):
    last_messages.pop(user_id, None)


def at_exit(user_id: int):
    set_user_state(user_id, UserState.NONE)
    clear_last_message(user_id)

@auth_router.message(Command("signup"))
async def signup(message: Message) -> None:
    logging.info(f"signup")
    button_cancel = InlineKeyboardButton(text="Cancel", callback_data=Callback.EXIT_FROM_REGISTERING)
    # button_prev = InlineKeyboardButton(text="Previous page", callback_data=Callback.PREVIOUS_PAGE_BET_MAKING)
    # button_next = InlineKeyboardButton(text="Next page", callback_data=Callback.NEXT_PAGE_BET_MAKING)


    markup = InlineKeyboardMarkup(inline_keyboard=[[button_cancel]])
    set_user_state(message.from_user.id, UserState.REGISTERING)
    answer = await message.answer(f"Sure!\n"
                                  f"Please, send your wallet address", reply_markup=markup)
    set_last_message(message.from_user.id, answer)


@auth_router.callback_query(F.data == Callback.EXIT_FROM_REGISTERING)
async def exit_from_registering(callback_query: CallbackQuery) -> None:
    logging.info(f"exit_from_registering")
    await callback_query.answer(f"Register cancelled...")
    deleted = await callback_query.message.delete()
    if not deleted:
        logging.critical(f"Could not delete bet making message")
    at_exit(callback_query.from_user.id)


@auth_router.message(lambda x: get_user_state(x.from_user.id) == UserState.REGISTERING)
async def sent_wallet_address(message: Message) -> None:
    logging.info(f"sent_wallet_address")
    button_cancel = InlineKeyboardButton(text="Cancel", callback_data=Callback.EXIT_FROM_REGISTERING)
    button_approve = InlineKeyboardButton(text="Approve", callback_data=Callback.APPROVE_REGISTER)

    address = message.text
    storage.registers[message.from_user.id] = address

    markup = InlineKeyboardMarkup(inline_keyboard=[[button_cancel, button_approve]])
    answer = await message.answer(f"Your wallet: {address}", reply_markup=markup)
    set_last_message(message.from_user.id, answer)

@auth_router.callback_query(F.data == Callback.APPROVE_REGISTER)
async def approve_register(callback_query: CallbackQuery) -> None:
    logging.info(f"approve_register")
    await callback_query.answer(f"Register approved...")

    storage.conn.register(callback_query.from_user.id, storage.registers[callback_query.from_user.id])

    edited = await callback_query.message.edit_text(f"Succesfully registered wallet {storage.registers[callback_query.from_user.id]} with ID: {callback_query.from_user.id}",
                                                    reply_markup=None)
    if isinstance(edited, bool):
        logging.critical(f"Could not edit bet making message")
    at_exit(callback_query.from_user.id)

@auth_router.message(Command("balance"))
async def balance(message: Message) -> None:
    logging.info(f"balance")

    user_balance = storage.conn.getBalance(message.from_user.id)

    answer = await message.answer(f"Your balance: {f'{user_balance:.18f}'.rstrip('0')} ETH", reply_markup=None)
