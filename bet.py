from dataclasses import dataclass, field


@dataclass
class BetOption:
    id: int = 0
    description: str = ""
    betters: dict[int, float] = field(default_factory=dict)


class Bet:
    def __init__(self, id_: int, description: str, options: list[str]):
        self.id: int = id_
        self.description: str = description
        self.option_1: BetOption = BetOption(0, options[0])
        self.option_2: BetOption = BetOption(1, options[1])

    def get_supply(self) -> int:
        supply = 0
        for wager in self.option_1.betters.values():
            supply += wager
        for wager in self.option_2.betters.values():
            supply += wager
        return supply

    def get_coeffs(self) -> tuple[float, float]:
        opt1_supply = 1
        for wager in self.option_1.betters.values():
            opt1_supply += wager
        opt2_supply = 1
        for wager in self.option_2.betters.values():
            opt2_supply += wager
        coeff1 = 1 + opt2_supply / opt1_supply
        coeff2 = 1 + opt1_supply / opt2_supply
        return coeff1, coeff2

    def get_bet_description(self) -> tuple[str, str, str]:
        return self.description, self.option_1.description, self.option_2.description

    def make_bet(self, better_id: int, amount: float, option_id: int) -> bool:
        if better_id in self.option_1.betters.keys() or option_id in self.option_2.betters.keys():
            return False
        if option_id == 0:
            self.option_1.betters[better_id] = amount
        else:
            self.option_2.betters[better_id] = amount
        return True

    def cancel_bet(self, better_id: int, option_id: int) -> bool:
        if option_id == 0:
            if better_id in self.option_1.betters.keys():
                self.option_1.betters.pop(better_id)
                return True
            else:
                return False
        else:
            if option_id in self.option_2.betters.keys():
                self.option_2.betters.pop(option_id)
                return True
            else:
                return False
