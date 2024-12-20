import json
import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from storage import storage
from user_states import UserState, set_user_state, get_user_state
from callbacks import Callback

bet_operations_router = Router(name=__name__)
last_messages: dict[int, Message] = {}
chosen_bets: dict[int, int] = {}
chosen_options: dict[int, int] = {}
chosen_ether_value: dict[int, float] = {}


def set_last_message(user_id: int, message: Message):
    last_messages[user_id] = message


def set_chosen_bet(user_id: int, chosen_bet: int):
    chosen_bets[user_id] = chosen_bet


def set_chosen_option(user_id: int, chosen_option: int):
    chosen_options[user_id] = chosen_option


def set_chosen_ether_value(user_id: int, ether_value: float):
    chosen_ether_value[user_id] = ether_value


def clear_last_message(user_id: int):
    last_messages.pop(user_id, None)


def clear_chosen_bet(user_id: int):
    chosen_bets.pop(user_id, None)


def clear_chosen_option(user_id: int):
    chosen_options.pop(user_id, None)


def clear_chosen_ether_value(user_id: int):
    chosen_ether_value.pop(user_id, None)


def at_exit(user_id: int):
    clear_last_message(user_id)
    clear_chosen_bet(user_id)
    clear_chosen_option(user_id)
    clear_chosen_ether_value(user_id)


@bet_operations_router.message(Command("make_bet_router"))
async def make_bet_router(message: Message):
    logging.info(f"view")
    _ = await message.answer(
        f"last_messages: {json.dumps({k: v.message_id for k, v in last_messages.items()}, indent=4)}\n"
        f"chosen_bets: {json.dumps(chosen_bets, indent=4)}\n"
        f"chosen_options: {json.dumps(chosen_options, indent=4)}\n"
        f"chosen_ether_value: {json.dumps(chosen_ether_value, indent=4)}\n")


@bet_operations_router.message(Command("make_bet"))
async def make_bet(message: Message) -> None:
    logging.info(f"make_bet")
    button_cancel = InlineKeyboardButton(text="Cancel", callback_data=Callback.EXIT_FROM_BET_MAKING)
    # button_prev = InlineKeyboardButton(text="Previous page", callback_data=Callback.PREVIOUS_PAGE_BET_MAKING)
    # button_next = InlineKeyboardButton(text="Next page", callback_data=Callback.NEXT_PAGE_BET_MAKING)

    # TODO: get list of active bet IDs from blockchain
    bet_ids = storage.bets.keys()
    buttons = []
    for bet_id in bet_ids:
        buttons += [[InlineKeyboardButton(text=storage.bets[bet_id].description,
                                          callback_data=Callback.SELECT_BET_ID + "_" + str(bet_id))]]
    markup = InlineKeyboardMarkup(inline_keyboard=[[button_cancel]] + buttons)
    set_user_state(message.from_user.id, UserState.CHOOSING_BET_ID)
    answer = await message.answer(f"Sure!\n"
                                  f"Please, select one of available bets:", reply_markup=markup)
    set_last_message(message.from_user.id, answer)


@bet_operations_router.callback_query(F.data == Callback.EXIT_FROM_BET_MAKING)
async def exit_from_bet_making(callback_query: CallbackQuery) -> None:
    logging.info(f"exit_from_bet_making")
    await callback_query.answer(f"Making bets cancelled...")
    deleted = await callback_query.message.delete()
    if not deleted:
        logging.critical(f"Could not delete bet making message")
    at_exit(callback_query.from_user.id)


@bet_operations_router.callback_query(F.data.startswith(Callback.SELECT_BET_ID))
async def selected_bet_id(callback_query: CallbackQuery) -> None:
    logging.info(f"selected_bet_id")
    await callback_query.answer(f"Selected bet...")

    bet_id = int(callback_query.data.split("_")[-1])
    set_chosen_bet(callback_query.from_user.id, bet_id)
    bet_info = storage.bets[bet_id]

    button_cancel = InlineKeyboardButton(text="Cancel", callback_data=Callback.EXIT_FROM_BET_MAKING)
    button_opt1 = InlineKeyboardButton(text=f"{bet_info.option_1.description}",
                                       callback_data=Callback.CHOSEN_BET_OPTION + "_0")
    button_opt2 = InlineKeyboardButton(text=f"{bet_info.option_2.description}",
                                       callback_data=Callback.CHOSEN_BET_OPTION + "_1")
    markup = InlineKeyboardMarkup(inline_keyboard=[[button_cancel], [button_opt1], [button_opt2]])

    op1_coeff, op2_coeff = bet_info.get_coeffs()
    edited = await callback_query.message.edit_text(f"Bet ID: {bet_id}\n"
                                                    f"{bet_info.description}\n"
                                                    f"--> {bet_info.option_1.description} (coeff: x{op1_coeff})\n"
                                                    f"--> {bet_info.option_2.description} (coeff: x{op2_coeff})",
                                                    reply_markup=markup)
    if isinstance(edited, bool):
        logging.critical(f"Could not edit bet making message")


@bet_operations_router.callback_query(F.data.startswith(Callback.CHOSEN_BET_OPTION))
async def selected_bet_id(callback_query: CallbackQuery) -> None:
    logging.info(f"selected_bet_id")
    await callback_query.answer(f"Selected bet...")

    bet_option = int(callback_query.data.split("_")[-1])
    set_chosen_option(callback_query.from_user.id, bet_option)
    bet_id = chosen_bets[callback_query.from_user.id]
    bet_info = storage.bets[bet_id]

    button_cancel = InlineKeyboardButton(text="Cancel", callback_data=Callback.EXIT_FROM_BET_MAKING)
    markup = InlineKeyboardMarkup(inline_keyboard=[[button_cancel]])

    # TODO get user balance here from blockchain
    user_balance = 1

    set_user_state(callback_query.from_user.id, UserState.CHOOSING_ETHER_AMOUNT_TO_BET)
    edited = await callback_query.message.edit_text(f"Bet ID: {bet_id}\n"
                                                    f"{bet_info.description}\n"
                                                    f"Chosen option --> {bet_info.get_bet_description()[bet_option + 1]}\n"
                                                    f"\n"
                                                    f"Please, enter how much ETH you want to bet\n"
                                                    f"User balance: {user_balance}", reply_markup=markup)
    if isinstance(edited, bool):
        logging.critical(f"Could not edit bet making message")


@bet_operations_router.message(lambda x: get_user_state(x.from_user.id) == UserState.CHOOSING_ETHER_AMOUNT_TO_BET)
async def chose_ether_amount_to_bet(message: Message) -> None:
    logging.info(f"chose_ether_amount_to_bet")
    button_cancel = InlineKeyboardButton(text="Cancel", callback_data=Callback.EXIT_FROM_BET_MAKING)
    button_approve = InlineKeyboardButton(text="Approve", callback_data=Callback.APPROVE_BET_MAKING)

    ether_amount = float(message.text)
    set_chosen_ether_value(message.from_user.id, ether_amount)
    bet_option = chosen_options[message.from_user.id]
    bet_id = chosen_bets[message.from_user.id]
    bet_info = storage.bets[bet_id]

    markup = InlineKeyboardMarkup(inline_keyboard=[[button_cancel, button_approve]])
    answer = await message.answer(f"Bet ID: {bet_id}\n"
                                  f"{bet_info.description}\n"
                                  f"Chosen option --> {bet_info.get_bet_description()[bet_option + 1]}\n"
                                  f"Bet size: {ether_amount} ETH", reply_markup=markup)
    set_last_message(message.from_user.id, answer)


@bet_operations_router.callback_query(F.data == Callback.APPROVE_BET_MAKING)
async def approve_bet_making(callback_query: CallbackQuery) -> None:
    logging.info(f"approve_bet_making")
    await callback_query.answer(f"Made bet...")

    ether_amount = chosen_ether_value[callback_query.from_user.id]
    bet_option = chosen_options[callback_query.from_user.id]
    bet_id = chosen_bets[callback_query.from_user.id]
    bet_info = storage.bets[bet_id]

    storage.user_wagers[callback_query.from_user.id] = (bet_id, bet_option, ether_amount)

    edited = await callback_query.message.edit_text(f"Succesfully betted {ether_amount} ETH with bet ID: {bet_id}\n"
                                                    f"{bet_info.description}\n"
                                                    f"On option --> {bet_info.get_bet_description()[bet_option + 1]}",
                                                    reply_markup=None)
    if isinstance(edited, bool):
        logging.critical(f"Could not edit bet making message")
    at_exit(callback_query.from_user.id)
