from __future__ import annotations

from typing import Optional, Tuple, List

from dataclasses import dataclass
import datetime


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



@dataclass(frozen=True)
class HistoryId:
    value: str


@dataclass(frozen=True)
class Balance:
    description: str
    date: datetime.date
    value: float
