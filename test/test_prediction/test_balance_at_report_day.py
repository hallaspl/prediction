import pytest
import datetime

from prediction import ReportDay, BalanceLogCalulator, Event, errors, Balance


def test_givenBalanceLogEmpty_whenBalanceAtReportDay_thenRaise():
    calculator = BalanceLogCalulator([])
    with pytest.raises(errors.CalculatorError):
        calculator.get_balance_at_report_day(ReportDay(month_day=10, description="Before PayDay"))


def test_whenNoReportDay_thenRaise():
    calculator = BalanceLogCalulator([])
    initial_balance = Balance(description="Initial balance", date=datetime.date(2022, 1, 1), value=111)
    calculator.get_balance_log(initial_balance)
    with pytest.raises(errors.CalculatorError):
        calculator.get_balance_at_report_day()


@pytest.mark.parametrize("report_day", (*list(range(1, 29)), -1))
def test_allowed_report_day_values(report_day: int):
    calculator = BalanceLogCalulator([])
    initial_balance = Balance(description="Initial balance", date=datetime.date(2022, 1, 1), value=111)
    calculator.get_balance_log(initial_balance)

    calculator.get_balance_at_report_day(ReportDay(month_day=report_day, description="test_allowed_report_day"))


@pytest.mark.parametrize("report_day", (29, 30, 31, -2, 0))
def test_not_allowd_report_day_values(report_day: int):
    calculator = BalanceLogCalulator([])
    initial_balance = Balance(description="Initial balance", date=datetime.date(2022, 1, 1), value=111)
    calculator.get_balance_log(initial_balance)
    with pytest.raises(errors.CalculatorError):
        calculator.get_balance_at_report_day(
            ReportDay(month_day=report_day, description="test_not_allowed_report_day")
        )


@pytest.mark.parametrize(
    "report_day, expected_date",
    (
        (ReportDay(month_day=12, description="Intial balance day"), datetime.date(2022, 3, 12)),
        (ReportDay(month_day=14, description="After initial balance day"), datetime.date(2022, 3, 14)),
        (ReportDay(month_day=7, description="Before initial balance day"), datetime.date(2022, 4, 7)),
    )
)
def test_emptyEvents_getCorrectReportDate(report_day: ReportDay, expected_date: datetime.date):
    calculator = BalanceLogCalulator([])
    initial_balance = Balance(description="Initial balance", date=datetime.date(2022, 3, 12), value=111)
    calculator.get_balance_log(initial_balance)

    balance_log = calculator.get_balance_at_report_day(report_day)

    final_balance = balance_log[0]
    assert final_balance.value == initial_balance.value
    assert final_balance.date == expected_date
    assert final_balance.description == report_day.description
    assert len(balance_log) == 1


def test_whenReportDateAfterAllEvents_thenOneBalance():
    calculator = BalanceLogCalulator(
        [
            Event(description="A", date=datetime.date(2022, 3, 22), balance_impact=-111),
        ]
    )
    initial_balance = Balance(description="Initial balance", date=datetime.date(2022, 3, 12), value=111)
    calculator.get_balance_log(initial_balance)

    balance_log = calculator.get_balance_at_report_day(ReportDay(month_day=23, description="Final balance"))

    final_balance = balance_log[0]
    assert final_balance.value == 0
    assert final_balance.date == datetime.date(2022, 3, 23)
    assert final_balance.description == "Final balance"
    assert len(balance_log) == 1


def test_whenReportDateBetweenDates_theneTwoBalance():
    calculator = BalanceLogCalulator(
        [
            Event(description="A", date=datetime.date(2022, 3, 22), balance_impact=-111),
        ]
    )
    initial_balance = Balance(description="Initial balance", date=datetime.date(2022, 3, 12), value=111)
    calculator.get_balance_log(initial_balance)

    balance_log = calculator.get_balance_at_report_day(ReportDay(month_day=18, description="Eigteenth"))

    first_balance = balance_log[0]
    assert first_balance.value == 111
    assert first_balance.date == datetime.date(2022, 3, 18)
    assert first_balance.description == "Eigteenth"
    final_balance = balance_log[1]
    assert final_balance.value == 0
    assert final_balance.date == datetime.date(2022, 4, 18)
    assert final_balance.description == "Eigteenth"
    assert len(balance_log) == 2


def test_whenNoEventsInMonthsAfterInitial_thenDupliaceInitalReportBalance():
    calculator = BalanceLogCalulator(
        [
            Event(description="B", date=datetime.date(2022, 12, 12), balance_impact=1_000),
        ]
    )
    initial_balance = Balance(description="Initial balance", date=datetime.date(2022, 3, 12), value=0)
    calculator.get_balance_log(initial_balance)

    balance_log = calculator.get_balance_at_report_day(ReportDay(month_day=25, description="25"))

    for idx, balance in enumerate(balance_log[:-1]):
        expected_month = 3 + idx
        assert balance.date.month == expected_month
        assert balance.date.day == 25
        assert balance.value == 0
    assert len(balance_log) == 10
    final_balance = balance_log[9]
    assert final_balance.value == 1_000
    assert final_balance.date == datetime.date(2022, 12, 25)


def test_givenMultipleEvents_whenNoEventsInOneMinth_duplicatePreviousBalance():
    calculator = BalanceLogCalulator(
        [
            Event(description="A", date=datetime.date(2022, 3, 22), balance_impact=-111),
            Event(description="B", date=datetime.date(2022, 4, 11), balance_impact=1_000),
            Event(description="C", date=datetime.date(2022, 5, 25), balance_impact=2_000),
            Event(description="D", date=datetime.date(2022, 6, 26), balance_impact=-4_000),
        ]
    )
    initial_balance = Balance(description="Initial balance", date=datetime.date(2022, 3, 12), value=111)
    calculator.get_balance_log(initial_balance)

    balance_log = calculator.get_balance_at_report_day(ReportDay(month_day=25, description="25"))

    first_balance = balance_log[0]
    assert first_balance.date == datetime.date(2022, 3, 25)
    assert first_balance.value == 0
    second_balance = balance_log[1]
    assert second_balance.date == datetime.date(2022, 4, 25)
    assert second_balance.value == 1_000
    third_balance = balance_log[2]
    assert third_balance.date == datetime.date(2022, 5, 25)
    assert third_balance.value == 3_000
    fourth_balance = balance_log[3]
    assert fourth_balance.date == datetime.date(2022, 6, 25)
    assert fourth_balance.value == 3_000
    final_balance = balance_log[4]
    assert final_balance.date == datetime.date(2022, 7, 25)
    assert final_balance.value == -1_000
    assert len(balance_log) == 5


def test_whenMultipleReportDays():
    calculator = BalanceLogCalulator(
        [
            Event(description="A", date=datetime.date(2022, 3, 22), balance_impact=-111),
            Event(description="B", date=datetime.date(2022, 4, 11), balance_impact=1_000),
            Event(description="C", date=datetime.date(2022, 5, 25), balance_impact=2_000),
            Event(description="D", date=datetime.date(2022, 6, 28), balance_impact=-4_000),
        ]
    )
    initial_balance = Balance(description="Initial balance", date=datetime.date(2022, 3, 12), value=111)
    calculator.get_balance_log(initial_balance)

    balance_log = calculator.get_balance_at_report_day(
        ReportDay(month_day=25, description="25"),
        ReportDay(month_day=26, description="26")
    )
    dates = [b.date for b in balance_log]
    assert dates == [
        datetime.date(2022, 3, 25),
        datetime.date(2022, 3, 26),
        datetime.date(2022, 4, 25),
        datetime.date(2022, 4, 26),
        datetime.date(2022, 5, 25),
        datetime.date(2022, 5, 26),
        datetime.date(2022, 6, 25),
        datetime.date(2022, 6, 26),
        datetime.date(2022, 7, 25),
        datetime.date(2022, 7, 26),
    ]

    # assert first_balance.date == datetime.date(2022, 3, 25)
    # assert first_balance.value == 0
    # second_balance = balance_log[1]
    # assert second_balance.date == datetime.date(2022, 4, 25)
    # assert second_balance.value == 1_000
    # third_balance = balance_log[2]
    # assert third_balance.date == datetime.date(2022, 5, 25)
    # assert third_balance.value == 3_000
    # fourth_balance = balance_log[3]
    # assert fourth_balance.date == datetime.date(2022, 6, 25)
    # assert fourth_balance.value == 3_000
    # final_balance = balance_log[4]
    # assert final_balance.date == datetime.date(2022, 7, 25)
    # assert final_balance.value == -1_000
    # assert len(balance_log) == 5
