from __future__ import annotations
import dataclasses as ds
from itertools import chain
from typing import List
from datetime import date
from .types import BalanceHistory, Comparition, Difference, Balance, Event


class ComparatorException(Exception):
    pass


class BaseIsEmpty(ComparatorException):
    pass


class HistoryComparator:
    def __init__(self, base: BalanceHistory, compared: BalanceHistory) -> None:
        self.__base = base
        self.__compared = compared
        self.__aligned_base: List[Event] = None
        self.__aligned_compared: List[Event] = None
        self.__common_dates: List[date] = []
        self.__first_date: date = None

    def compare(self) -> Comparition:
        try:
            self.__first_date = max(self.__base.balances[0].date, self.__compared.balances[0].date)
        except IndexError:
            return Comparition(diffs=[], base_id=self.__base.id, compared_id=self.__compared.id)
        self.__fill_common_dates()
        self.__aligned_base = self.__align_first_balance(self.__base.balances)
        self.__aligned_base = self.__align_to_common_dates(self.__aligned_base)
        self.__aligned_compared = self.__align_first_balance(self.__compared.balances)
        self.__aligned_compared = self.__align_to_common_dates(self.__aligned_compared)
        differences = []
        for base, compared in zip(self.__aligned_base, self.__aligned_compared):
            if base.date < self.__first_date:
                continue
            assert base.date == compared.date, f"{base}, {compared}"
            diff = Difference(date=base.date, value=compared.value - base.value)
            differences.append(diff)
        return Comparition(
            diffs=differences, base_id=self.__base.id, compared_id=self.__compared.id
        )

    def __fill_common_dates(self) -> None:
        dates = chain((b.date for b in self.__base.balances), (c.date for c in self.__compared.balances))
        dates_set = set(dates)
        self.__common_dates = list(d for d in dates_set if d >= self.__first_date)
        self.__common_dates.sort()

    def __align_first_balance(self, balances: List[Balance]) -> List[Balance]:
        n_skipped = 0
        first_balance = None
        for bal in balances:
            if bal.date <= self.__first_date:
                first_balance = ds.replace(bal, date=self.__first_date)
                n_skipped += 1
        if first_balance:
            return [first_balance] + balances[n_skipped:]
        return balances

    def __align_to_common_dates(self, source: List[Balance]) -> List[Balance]:
        aligned = []
        balance_idx = 0
        date_idx = 0
        prev_bal = None
        while True:
            try:
                bal = source[balance_idx]
            except IndexError:
                bal = prev_bal
            try:
                current = self.__common_dates[date_idx]
            except IndexError:
                break
            if bal.date == current:
                aligned.append(bal)
                prev_bal = bal
                balance_idx += 1
            if bal.date < current:
                aligned.append(ds.replace(bal, date=current))
            elif bal.date > current:
                aligned.append(ds.replace(prev_bal, date=current))
            date_idx += 1
        return aligned
