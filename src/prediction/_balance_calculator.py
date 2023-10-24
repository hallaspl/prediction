from __future__ import annotations
from typing import List, Optional
import dataclasses
import datetime
import calendar

from .types import Event, Balance
from .errors import CalculatorError
from ._helpers import increase_date_by_one_month


@dataclasses.dataclass
class ReportDay:
    month_day: int
    description: str


class BalanceLogCalulator:
    @dataclasses.dataclass
    class __ReportData:
        description: str
        balance: Optional[Balance] = None
        date: Optional[datetime.date] = None

    def __init__(self, events: List[Event]) -> None:
        self.__events = events
        self.__balance_log: List[Balance] = []
        self.__calendar = calendar.Calendar()

    def get_balance_at_report_day(self, *report_days: ReportDay) -> List[Balance]:
        if not self.__balance_log:
            raise CalculatorError("Balance log not calulated. Run 'get_balance_log' first")
        if len(report_days) < 1:
            raise CalculatorError("No report days provided")
        for day in report_days:
            self.__validate_report_day(day)
        result = list()
        for day in report_days:
            result += self.__get_balance_at_report_day(day)
        result.sort(key=lambda b: b.date)
        return result

    def __get_balance_at_report_day(self, report_day: ReportDay) -> List[Balance]:
        result = list()
        next_report = self.__ReportData(description=report_day.description)
        for balance in self.__balance_log:
            if next_report.date is None:
                next_report = self.__cretate_report_data(balance, report_day)
            elif balance.date <= next_report.date:
                next_report.balance = balance
            else:
                result.append(self.__create_report_balance(next_report))
                next_report = self.__cretate_report_data(balance, report_day)
                result += self.__duplicate_report_balance(result[-1], next_report.date)
        if next_report.balance is not None:
            result.append(self.__create_report_balance(next_report))
        return result

    def __cretate_report_data(self, balance: Balance, report_day: ReportDay) -> __ReportData:
        return self.__ReportData(
            description=report_day.description,
            balance=balance,
            date=self.__get_report_date(balance.date, report_day.month_day)
        )

    def __create_report_balance(self, report_state: __ReportData) -> Balance:
        return dataclasses.replace(report_state.balance, date=report_state.date, description=report_state.description)

    def __duplicate_report_balance(self, balance: Balance, next_change_date: datetime.date) -> List[Balance]:
        result = []
        time_delta = next_change_date - balance.date
        while time_delta.days > 31:
            balance = dataclasses.replace(balance, date=increase_date_by_one_month(balance.date))
            result.append(balance)
            time_delta = next_change_date - balance.date
        return result

    def __get_report_date(self, date: datetime.date, report_day: int) -> datetime.date:
        if report_day == -1:
            report_day = max(self.__calendar.itermonthdays(date.year, date.month))
        result = date.replace(day=report_day)
        if result < date:
            return increase_date_by_one_month(result)
        return result

    def __validate_report_day(self, report_day: ReportDay) -> None:
        if report_day.month_day > 28 or report_day.month_day < -1 or report_day.month_day == 0:
            raise CalculatorError(
                f"Month end day={report_day.month_day} is not alowed. Try numbers from[1, ..., 28] or -1."
            )

    def get_balance_log(self, initial: Balance) -> List[Balance]:
        self.__balance_log = [initial]
        for event in self.__events:
            self.__process_event(event)
        return self.__balance_log

    def __process_event(self, event: Event) -> None:
        previous_balance = self.__balance_log[-1]
        if event.date < previous_balance.date:
            return
        value = previous_balance.value + event.balance_impact
        if event.date == previous_balance.date:
            self.__balance_log[-1] = Balance(
                description=previous_balance.description + ", " + event.description,
                date=event.date,
                value=value
            )
            return
        self.__balance_log.append(Balance(description=event.description, date=event.date, value=value))
