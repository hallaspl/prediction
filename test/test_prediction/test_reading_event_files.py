import datetime
import os

from prediction import (
    EventData,
    MonthlyEventData,
    EventsFileReader,
    line_to_event,
    line_to_monthly_event,
)


def test_read_all_files_in_data_folder(example_data_folder_path: str):
    for file_name in os.listdir(example_data_folder_path):
        assert file_name.endswith(".csv")
        file_path = os.path.join(example_data_folder_path, file_name)
        if file_name.startswith("monthly"):
            reader = EventsFileReader[MonthlyEventData](path=file_path, transform_func=line_to_monthly_event)
            events = reader.read()
            assert len(events) > 0
            for e in events:
                assert_monthly_event(e)
        elif file_name.startswith("one_time"):
            reader = EventsFileReader[EventData](path=file_path, transform_func=line_to_event)
            events = reader.read()
            assert len(events) > 0
            for e in events:
                assert_one_time_event(e)


def assert_one_time_event(event: EventData) -> None:
    assert isinstance(event, EventData)
    assert event.value > 0
    assert event.description
    assert isinstance(event.date, datetime.date)


def assert_monthly_event(event: MonthlyEventData) -> None:
    assert isinstance(event, MonthlyEventData)
    assert event.value > 0
    assert event.description
    assert isinstance(event.start_date, datetime.date)
    assert event.month_day == event.start_date.day
    if event.end_date is not None:
        assert isinstance(event.end_date, datetime.date)
        assert event.start_date <= event.end_date
        assert event.end_date.day == event.start_date.day
