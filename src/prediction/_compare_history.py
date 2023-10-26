from __future__ import annotations
from datetime import date
from .types import BalanceHistory, Comparition, Difference


class HistoryComparator:
    def __init__(self, base: BalanceHistory, compared: BalanceHistory) -> None:
        self.__base = base
        self.__compared = compared

    def compare(self) -> Comparition:
        histories_are_empty = (
            not self.__base.balances
            and not self.__compared.balances
        )
        if histories_are_empty:
            return Comparition(diffs=[])
        base_balance = self.__base.balances[0]
        compared_balance = self.__compared.balances[0]
        if base_balance.date < compared_balance.date:
            value = compared_balance.value - base_balance.value
            diff = Difference(compared_balance.date, value)
        if compared_balance.date < base_balance.date:
            value = compared_balance.value - base_balance.value
            diff = Difference(base_balance.date, value)
        return Comparition(diffs=[diff])
        
        
        

