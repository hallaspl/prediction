import datetime

from prediction import BalanceLogCalulator, Balance, Event


def test_initial_balance_when_no_events():
    calculator = BalanceLogCalulator([])
    intial_balance = Balance(description="Initial balance", date=datetime.date(2022, 4, 11), value=1002)

    balance = calculator.get_balance_log(intial_balance)

    assert len(balance) == 1
    assert balance[0] == intial_balance


def test_events_before_inital_date_are_ignored():
    calculator = BalanceLogCalulator(
        [
            Event(description="A", date=datetime.date(2022, 1, 10), balance_impact=231),
            Event(description="B", date=datetime.date(2022, 2, 10), balance_impact=231),
            Event(description="C", date=datetime.date(2022, 3, 10), balance_impact=231),
            Event(description="D", date=datetime.date(2022, 4, 12), balance_impact=400),
        ]
    )
    intial_balance = Balance(description="Initial balance", date=datetime.date(2022, 4, 11), value=1002)

    balance_log = calculator.get_balance_log(intial_balance)

    assert len(balance_log) == 2
    assert balance_log[0] == intial_balance
    assert balance_log[1].description == "D"


def test_whenOneEvent_thenTwoBalance():
    single_event = Event(description="", date=datetime.date(2023, 4, 10), balance_impact=-1000)
    calculator = BalanceLogCalulator([single_event])
    intial_balance = Balance(description="Initial balance", date=datetime.date(2022, 4, 11), value=1002)

    balance_log = calculator.get_balance_log(intial_balance)

    assert len(balance_log) == 2
    assert balance_log[0] == intial_balance
    second_balance = balance_log[1]
    assert second_balance.description == single_event.description
    assert second_balance.date == single_event.date
    assert second_balance.value == 2


def test_whenTwoEvents_thenThreeBalance():
    first_event = Event(description="", date=datetime.date(2023, 4, 10), balance_impact=-1000)
    second_event = Event(description="", date=datetime.date(2023, 5, 10), balance_impact=-2000)
    intial_balance = Balance(description="Initial balance", date=datetime.date(2022, 4, 11), value=3002)
    calculator = BalanceLogCalulator([first_event, second_event])

    balance_log = calculator.get_balance_log(intial_balance)

    assert len(balance_log) == 3
    last_balance = balance_log[-1]
    assert last_balance.date == second_event.date
    assert last_balance.value == 2


def test_whenEventsSameDate_thenReduceBalanceCount():
    first_event = Event(description="A", date=datetime.date(2023, 4, 10), balance_impact=-1)
    second_event = Event(description="B", date=datetime.date(2023, 4, 10), balance_impact=-2)
    intial_balance = Balance(description="I", date=datetime.date(2023, 4, 10), value=5)

    calculator = BalanceLogCalulator([first_event, second_event])

    balance_log = calculator.get_balance_log(intial_balance)
    assert len(balance_log) == 1
    one_balance = balance_log[0]
    assert one_balance.date == intial_balance.date
    assert one_balance.value == 2
    assert one_balance.description == "I, A, B"
