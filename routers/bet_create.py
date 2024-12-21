import json
import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from bet import Bet
from storage import storage
from user_states import UserState, set_user_state, get_user_state, user_states
from callbacks import Callback

bet_create_router = Router(name=__name__)
last_messages: dict[int, Message] = {}
bet_cache: dict[int, list[str]] = {}


def set_last_message(user_id: int, message: Message):
    last_messages[user_id] = message


def clear_last_message(user_id: int):
    last_messages.pop(user_id, None)


def clear_bet_cache(user_id: int):
    bet_cache.pop(user_id, None)


def at_exit(user_id: int):
    clear_last_message(user_id)
    clear_bet_cache(user_id)
    set_user_state(user_id, UserState.NONE)


@bet_create_router.message(Command("create_bet_sudo"))
async def view(message: Message) -> None:
    logging.info(f"view")
    _ = await message.answer(
        f"last_messages: {json.dumps({k: v.message_id for k, v in last_messages.items()}, indent=4)}\n"
        f"bet_cache: {json.dumps(bet_cache, indent=4)}\n"
        f"statuses: {json.dumps(user_states, indent=4)}\n")


@bet_create_router.message(Command("create_bet"))
async def create_bet(message: Message) -> None:
    logging.info(f"create_bet")
    button = InlineKeyboardButton(text="Cancel", callback_data=Callback.EXIT_FROM_BET_CREATION)
    markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
    set_user_state(message.from_user.id, UserState.CREATING_BET_DESCRIPTION)
    answer = await message.answer(f"Sure!\n"
                                  f"Please, enter bet description:", reply_markup=markup)
    set_last_message(message.from_user.id, answer)


@bet_create_router.callback_query(F.data == Callback.EXIT_FROM_BET_CREATION)
async def exit_from_bet_creation(callback_query: CallbackQuery) -> None:
    logging.info(f"create_bet_exit")
    await callback_query.answer(f"Creation cancelled...")
    deleted = await callback_query.message.delete()
    if not deleted:
        logging.critical(f"Could not delete bet creation message")
    at_exit(callback_query.from_user.id)


@bet_create_router.message(lambda x: get_user_state(x.from_user.id) == UserState.CREATING_BET_DESCRIPTION)
async def suggest_filling_options(message: Message) -> None:
    logging.info(f"suggest_filling_options")
    button = InlineKeyboardButton(text="Cancel", callback_data=Callback.EXIT_FROM_BET_CREATION)
    markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
    set_user_state(message.from_user.id, UserState.ADDING_BET_OPTIONS)
    deleted = await last_messages[message.from_user.id].delete_reply_markup()
    if not deleted:
        logging.critical(f"Could not delete bet options message")
    bet_cache[message.from_user.id] = [message.text]
    answer = await message.answer(f"Added bet \"{message.text}\".\n"
                                  f"Please, add at least 2 options:", reply_markup=markup)
    set_last_message(message.from_user.id, answer)


@bet_create_router.message(lambda x: get_user_state(x.from_user.id) == UserState.ADDING_BET_OPTIONS)
async def add_option_to_bet(message: Message) -> None:
    logging.info(f"add_option_to_bet")
    if len(bet_cache[message.from_user.id]) == 3:
        await message.delete()
        return
    deleted = await last_messages[message.from_user.id].delete_reply_markup()
    if not deleted:
        logging.critical(f"Could not delete bet options message")
    bet_cache[message.from_user.id] += [message.text]
    if len(bet_cache[message.from_user.id]) == 2:
        button = InlineKeyboardButton(text="Return", callback_data=Callback.EXIT_FROM_BET_CREATION)
        markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
        answer = await message.answer(f"Bet \"{bet_cache[message.from_user.id][0]}\".\n"
                                      f"--> {bet_cache[message.from_user.id][1]}\n"
                                      f"Please, add one more option:", reply_markup=markup)
    else:
        button_yes = InlineKeyboardButton(text="Yes", callback_data=Callback.PROCEED_WITH_BET_CREATION)
        button_no = InlineKeyboardButton(text="No", callback_data=Callback.DISCARD_BET_CREATION)
        markup = InlineKeyboardMarkup(inline_keyboard=[[button_yes, button_no]])
        answer = await message.answer(f"Bet \"{bet_cache[message.from_user.id][0]}\".\n"
                                      f"--> {bet_cache[message.from_user.id][1]}\n"
                                      f"--> {bet_cache[message.from_user.id][2]}\n"
                                      f"Do you want to proceed?", reply_markup=markup)
    set_last_message(message.from_user.id, answer)


@bet_create_router.callback_query(F.data == Callback.PROCEED_WITH_BET_CREATION)
async def proceed_with_bet_creation(callback_query: CallbackQuery) -> None:
    logging.info(f"proceed_with_bet_creation")
    await callback_query.answer(f"Creation approved...")

    _ = storage.conn.createBet()
    bet_id = len(storage.bets) + 1
    storage.bets[bet_id] = Bet(bet_id, bet_cache[callback_query.from_user.id][0], [bet_cache[callback_query.from_user.id][1], bet_cache[callback_query.from_user.id][2]])

    edit = await callback_query.message.edit_text(f"Bet was created! ID: {bet_id}", reply_markup=None)
    if isinstance(edit, bool):
        logging.critical(f"Could not edit bet creation message")
    at_exit(callback_query.from_user.id)


@bet_create_router.callback_query(F.data == Callback.DISCARD_BET_CREATION)
async def discard_bet_creation(callback_query: CallbackQuery) -> None:
    logging.info(f"discard_bet_creation")
    await callback_query.answer(f"Creation cancelled...")
    edit = await callback_query.message.edit_text(f"Bet was discarded!", reply_markup=None)
    if isinstance(edit, bool):
        logging.critical(f"Could not edit bet creation message")
    at_exit(callback_query.from_user.id)
