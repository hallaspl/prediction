import datetime
import dataclasses
import os
from typing import List, Optional

from .types import ScenarioConfiguration, DataSourcesConfiguration, EventsDataPaths, Balance
from ._balance_calculator import BalanceLogCalulator, ReportDay
from ._event_generator import EventGenerator
from ._data_loader import line_to_balance, EventsFileReader
from .cli import BalanceLogPrinter


MONTHLY = "m"
ONE_TIME = "o"
SPENDING = "s"
INCOME = "i"


@dataclasses.dataclass
class MainCfg:
    start_balance: float
    end_date: datetime.date
    start_date: Optional[datetime.date] = datetime.date.today()
    report_days: List[ReportDay] = dataclasses.field(default_factory=list)


def show_balance(config: MainCfg, event_gen: EventGenerator) -> None:
    # TODO: change to func accepting file-like object to make it possible to print into file or another terminal
    scenario_config = ScenarioConfiguration(
        start_date=config.start_date, end_date=config.end_date,
    )
    events = event_gen.get_events(scenario_config)
    calculator = BalanceLogCalulator(events)
    balance_log = calculator.get_balance_log(Balance("Initial", config.start_date, config.start_balance))
    if config.report_days:
        balance_log = calculator.get_balance_at_report_day(*config.report_days)
    # TODO: Test event gen and crate event printer
    print("Skipped Events:")
    for e in event_gen.get_skipped_events():
        print(e)
    print("Balance Log:")  # TODO: move to balance log printer
    BalanceLogPrinter(balance_log).print_all()


def build_data_sources_configuration(folder_path: str) -> DataSourcesConfiguration:
    monthly_spending_paths = []
    monthly_income_paths = []
    one_time_spending_paths = []
    one_time_income_paths = []
    for name in os.listdir(folder_path):
        is_monthly = name[0] == MONTHLY
        is_one_time = name[0] == ONE_TIME
        is_spending = name[1] == SPENDING
        is_income = name[1] == INCOME
        file_path = os.path.join(folder_path, name)
        if is_monthly and is_spending:
            monthly_spending_paths.append(file_path)
        if is_monthly and is_income:
            monthly_income_paths.append(file_path)
        if is_one_time and is_spending:
            one_time_spending_paths.append(file_path)
        if is_one_time and is_income:
            one_time_income_paths.append(file_path)
    return DataSourcesConfiguration(
        monthly_spending_paths=EventsDataPaths(monthly_spending_paths),
        monthly_income_paths=EventsDataPaths(monthly_income_paths),
        one_time_income_paths=EventsDataPaths(one_time_income_paths),
        one_time_spending_paths=EventsDataPaths(one_time_spending_paths),
    )


def read_initial_balance(file_path: str) -> float:
    reader = EventsFileReader[Balance](file_path, line_to_balance)
    result = 0
    for balance in reader.read():
        result += balance.value
    return result
