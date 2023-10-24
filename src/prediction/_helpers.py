import datetime


def increase_date_by_one_month(date: datetime.date) -> datetime.date:
    next_month = date.month + 1
    if next_month < 13:
        return datetime.date.replace(date, month=next_month)
    return datetime.date.replace(date, year=date.year + 1, month=1)
