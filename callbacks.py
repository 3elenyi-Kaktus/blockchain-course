from enum import Enum


class Callback(str, Enum):
    EXIT_FROM_BET_CREATION = "exit_from_bet_creation"
    DISCARD_BET_CREATION = "discard_bet_creation"
    PROCEED_WITH_BET_CREATION = "proceed_with_bet_creation"

    EXIT_FROM_BET_MAKING = "exit_from_bet_making"
    SELECT_BET_ID = "select_bet_id"
    # PREVIOUS_PAGE_BET_MAKING = "previous_page_bet_making"
    # NEXT_PAGE_BET_MAKING = "next_page_bet_making"
    CHOSEN_BET_OPTION = "chosen_bet_option"
    APPROVE_BET_MAKING = "approve_bet_making"
