from __future__ import annotations
from typing import List
from datetime import date
from .types import BalanceHistory, Comparition, Difference, Balance


class HistoryComparator:
    def __init__(self, base: BalanceHistory, compared: BalanceHistory) -> None:
        self.__base = base
        self.__compared = compared
        self.__n_compared = 0

    def compare(self) -> Comparition:
        differences = []
        for balance, next_balance in zip(self.__base.balances[:-1], self.__base.balances[1:]):
            differences += self.__diffs_in_span(balance, next_balance)
        if self.__base.balances:
            last_balance = self.__base.balances[-1]
            to_compare = self.__compared.balances[self.__n_compared:]
            to_compare = self.__remove_past_balances(to_compare, last_balance.date)
            differences += self.__diffs_to_balance(last_balance, to_compare)
        return Comparition(diffs=differences)
    
    def __remove_past_balances(self, to_compare: List[Balance], start_date: date) -> List[Balance]:
        for idx, balance in enumerate(to_compare):
            if balance.date >= start_date:
                return to_compare[idx:]
        return to_compare[-1:]
        

    def __diffs_in_span(self, start_balance: Balance, end_balance: Balance) -> List[Difference]:
        diffs = []
        to_compare = self.__to_compare_in_timespan(start_balance.date, end_balance.date)
        diffs += self.__diffs_to_balance(start_balance, to_compare)
        next_compared = self.__compared.balances[self.__n_compared]
        if next_compared.date > end_balance.date:
            last_compared = self.__compared.balances[self.__n_compared - 1]
            end_diff = Difference(end_balance.date, last_compared.value - end_balance.value)
            diffs.append(end_diff)
        return diffs

    def __to_compare_in_timespan(self, start_date: date, end_date: date) -> List[Balance]:
        to_compare = []
        for balance in self.__compared.balances[self.__n_compared:]:
            if start_date < balance.date < end_date:
                to_compare.append(balance)
        return to_compare

    def __diffs_to_balance(self, base_balance: Balance, to_compare: List[Balance]) -> List[Difference]:
        result = []
        for compared in to_compare:
            diff_date = max(base_balance.date, compared.date)
            diff = Difference(diff_date, compared.value - base_balance.value)
            self.__n_compared += 1
            result.append(diff)
        return result
