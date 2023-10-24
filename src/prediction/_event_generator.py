import datetime
import dataclasses
from typing import List, Iterable, Optional

from .types import (
    DataSourcesConfiguration,
    EventData,
    MonthlyEventData,
    Event,
    ScenarioConfiguration,
)
from ._validation import validate_event_data, validate_monthly_event_data
from ._data_loader import EventsFileReader, line_to_event, line_to_monthly_event
from ._helpers import increase_date_by_one_month


class EventGenerator:
    def __init__(self, config: DataSourcesConfiguration) -> None:
        self.__one_time_spending_readers = [
            EventsFileReader[EventData](path=p, transform_func=line_to_event)
            for p in config.one_time_spending_paths.paths
        ]
        self.__one_time_income_readers = [
            EventsFileReader[EventData](path=p, transform_func=line_to_event)
            for p in config.one_time_income_paths.paths
        ]
        self.__monthly_spending_readers = [
            EventsFileReader[MonthlyEventData](path=p, transform_func=line_to_monthly_event)
            for p in config.monthly_spending_paths.paths
        ]
        self.__monthly_income_readers = [
            EventsFileReader[MonthlyEventData](path=p, transform_func=line_to_monthly_event)
            for p in config.monthly_income_paths.paths
        ]
        self.__paid_events = []
        self.__skipped_events = []

    def get_events(self, config: ScenarioConfiguration) -> List[Event]:
        events = []
        events += self.__get_monthly_events(self.__monthly_spending_readers, config, is_income=False)
        events += self.__get_monthly_events(self.__monthly_income_readers, config, is_income=True)
        events += self.__get_one_time_events(self.__one_time_income_readers, config, is_income=True)
        events += self.__get_one_time_events(self.__one_time_spending_readers, config, is_income=False)
        events.sort(key=lambda e: e.date)
        return events

    def get_paid_events(self) -> List[Event]:
        return self.__paid_events

    def get_skipped_events(self) -> List[Event]:
        return self.__skipped_events

    def __get_one_time_events(
        self, readers_iter: Iterable[EventsFileReader], config: ScenarioConfiguration, is_income: bool
    ) -> List[Event]:
        events = []
        for reader in readers_iter:
            for event_data in reader.read():
                validate_event_data(event_data)
                new_event = Event(
                    description=event_data.description,
                    date=event_data.date,
                    balance_impact=event_data.value if is_income else -event_data.value
                )
                if event_data.paid:
                    self.__paid_events.append(new_event)
                elif config.start_date <= event_data.date <= config.end_date:
                    events.append(new_event)
                else:
                    self.__skipped_events.append(new_event)
        return events

    def __get_monthly_events(
        self, readers_iter: Iterable[EventsFileReader], config: ScenarioConfiguration, is_income: bool
    ) -> List[Event]:
        events = []
        for reader in readers_iter:
            for monthly_event in reader.read():
                validate_monthly_event_data(monthly_event)
                event_template = Event(
                    description=monthly_event.description,
                    date=self.__get_first_repetition_date(config.start_date, monthly_event.start_date),
                    balance_impact=monthly_event.value if is_income else -monthly_event.value
                )
                duplicate_end_date = self.__get_last_repetition_date(config.end_date, monthly_event.end_date)
                events += self.__repeat_montly_event(event_template, duplicate_end_date)
        return events

    def __get_first_repetition_date(
        self, config_start_date: datetime.date, event_start_date: Optional[datetime.date]
    ) -> datetime.date:
        while event_start_date < config_start_date:
            event_start_date = increase_date_by_one_month(event_start_date)
        return event_start_date

    def __get_last_repetition_date(
        self, config_end_date: datetime.date, event_end_date: Optional[datetime.date]
    ) -> datetime.date:
        if event_end_date is None:
            return config_end_date
        return min(config_end_date, event_end_date)

    def __repeat_montly_event(self, event_template: Event, end_date: datetime.date) -> List[Event]:
        log = []
        while event_template.date <= end_date:
            log.append(event_template)
            event_template = dataclasses.replace(
                event_template, date=increase_date_by_one_month(event_template.date)
            )
        return log
