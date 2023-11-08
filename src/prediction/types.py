from __future__ import annotations

from typing import Optional, Tuple, List

from dataclasses import dataclass
import datetime
from .errors import ValidationError


@dataclass(frozen=True)
class EventData:
    description: str
    value: float
    date: date
    paid: bool = False


@dataclass(frozen=True)
class MonthlyEventData:
    description: str
    value: float
    start_date: datetime.date
    end_date: Optional[datetime.date]
    month_day: int


@dataclass(frozen=True)
class DataSourcesConfiguration:
    monthly_spending_paths: EventsDataPaths
    one_time_spending_paths: EventsDataPaths
    monthly_income_paths: EventsDataPaths
    one_time_income_paths: EventsDataPaths


@dataclass(frozen=True)
class ScenarioConfiguration:
    start_date: datetime.date
    end_date: datetime.date


@dataclass(frozen=True)
class EventsDataPaths:
    paths: Tuple[str]


@dataclass(frozen=True)
class Event:
    description: str
    date: datetime.date
    balance_impact: float


@dataclass(frozen=True)
class BalanceHistory:
    id: HistoryId
    balances: List[Balance]

    def __post_init__(self) -> None:
        for previous, next in zip(self.balances[:-1], self.balances[1:]):
            if previous.date > next.date:
                raise ValidationError("balances dates are descending")


@dataclass(frozen=True)
class HistoryId:
    value: str


@dataclass(frozen=True)
class Balance:
    description: str
    date: datetime.date
    value: float


@dataclass(frozen=True)
class Comparition:
    base_id: HistoryId
    compared_id: HistoryId
    diffs: List[Difference]


@dataclass(frozen=True)
class Difference:
    date: datetime.date
    value: float
