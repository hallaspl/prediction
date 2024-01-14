from typing import List, Generic, TypeVar, Callable
import datetime
import os

from .types import EventData, MonthlyEventData, Balance


T = TypeVar("T")


_SEP = ";"
_DATE_SEP = "."


def line_to_balance(line: str) -> Balance:
    data = line.split(_SEP)
    description = data[0].strip()
    value = float(data[1].strip())
    return Balance(description=description, value=value, date=datetime.date.today())


def line_to_event(line: str) -> EventData:
    data = line.split(_SEP)
    description = data[0].strip()
    value = float(data[1].strip())
    date_str = data[2].strip()
    try:
        paid = bool(data[3])
    except IndexError:
        paid = False
    return EventData(
        description=description,
        value=value,
        date=__date_str_to_date(date_str),
        paid=paid
    )


def line_to_monthly_event(line: str) -> MonthlyEventData:
    data = line.split(_SEP)
    description = data[0].strip()
    value = float(data[1].strip())
    start_date = __date_str_to_date(data[2].strip())
    try:
        end_date_str = data[3].strip()
    except IndexError:
        end_date = None
    else:
        end_date = __date_str_to_date(end_date_str)
    return MonthlyEventData(
        description=description,
        value=value,
        start_date=start_date,
        end_date=end_date,
        month_day=start_date.day
    )


def __date_str_to_date(date_str: str) -> datetime.date:
    data = date_str.split(_DATE_SEP)
    year = int(data[0])
    month = int(data[1])
    day = int(data[2])
    return datetime.date(year=year, month=month, day=day)


class EventsFileReader(Generic[T]):
    def __init__(self, path: str, transform_func: Callable[[str], T]) -> None:
        self.__path = os.path.realpath(path)
        self.__transform_func = transform_func

    def read(self) -> List[T]:
        events = []
        with open(self.__path) as file:
            for line in file.readlines()[1:]:
                line = line.strip()
                if line:
                    new_event = self.__new_event(line)
                    events.append(new_event)
        return events
    
    def __new_event(self, line: str) -> T:
        try:
            return self.__transform_func(line)
        except ValueError as err:
            raise RuntimeError(f"Error during processing line: {line}") from err
