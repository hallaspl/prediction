import datetime

from .types import EventData, MonthlyEventData
from .errors import ValidationError


def validate_event_data(event: EventData) -> None:
    if (
        not isinstance(event, EventData)
        or event.value <= 0
        or not event.description
        or not isinstance(event.date, datetime.date)
    ):
        raise ValidationError(event)


def validate_monthly_event_data(event: MonthlyEventData) -> None:
    if (
        not isinstance(event, MonthlyEventData)
        or event.value <= 0
        or not event.description
        or not isinstance(event.start_date, datetime.date)
        or event.month_day != event.start_date.day
    ):
        raise ValidationError(event)
    if event.end_date is not None:
        if (
            not isinstance(event.end_date, datetime.date)
            or event.start_date > event.end_date
            or event.end_date.day != event.start_date.day
        ):
            raise ValidationError(event)
