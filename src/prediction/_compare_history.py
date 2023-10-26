from __future__ import annotations
from typing import List
from datetime import datetime
from dataclasses import dataclass
from .types import BalanceHistory


@dataclass(frozen=True)
class Comparition:
    diffs: List[Difference]


@dataclass(frozen=True)
class Difference:
    date: datetime.date
    value: float


class HistoryComparator:
    def __init__(self, base: BalanceHistory, compared: BalanceHistory) -> None:
        self.__base = base
        self.__compared = compared

    def compare(self) -> Comparition:
        return Comparition(diffs=[])
