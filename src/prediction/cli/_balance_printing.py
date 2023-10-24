from typing import List

from ..types import Balance


class BalanceLogPrinter:
    def __init__(self, balance_log: List[Balance]) -> None:
        self.__balance_log = balance_log
        self.__value_length = max(len(str(b.value)) for b in self.__balance_log)

    def print_all(self) -> None:
        for balance in self.__balance_log:
            print(self.__get_one_line_balance(balance))

    def __get_one_line_balance(self, balance: Balance) -> str:
        value_str = f"{balance.value:_.0f}"
        return f"{balance.date} | {value_str.rjust(self.__value_length)} | {balance.description}"
