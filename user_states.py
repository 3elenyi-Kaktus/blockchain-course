from enum import Enum


class UserState(str, Enum):
    NONE = "none"
    CREATING_BET_DESCRIPTION = "creating_bet_description"
    ADDING_BET_OPTIONS = "adding_bet_options"

    MAKING_BET = "making_bet"
    CHOOSING_BET_ID = "choosing_bet_id"
    CHOOSING_ETHER_AMOUNT_TO_BET = "choosing_ether_amount_to_bet"

    REGISTERING = "registering"



user_states: dict[int, UserState] = {}

def set_user_state(user_id: int, state: UserState) -> None:
    user_states[user_id] = state

def get_user_state(user_id: int) -> UserState:
    return user_states.get(user_id, None)