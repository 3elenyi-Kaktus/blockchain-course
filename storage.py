from bet import Bet
from conn import Connector


class Storage:
    def __init__(self):
        self.bets: dict[int, Bet] = {} #{0: Bet(0, "Test tot", ["op1", "op2"])}
        self.user_wagers: dict[int, tuple[int, int, float]] = {}
        self.user_balances: dict[int, float] = {}
        self.registers: dict[int, str] = {}
        self.conn = Connector()

storage: Storage = Storage()