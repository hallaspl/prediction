import pytest
import datetime
import os
from collections import namedtuple

from prediction import EventGenerator, DataSourcesConfiguration, EventsDataPaths, ScenarioConfiguration


def test_empty_conifg_produces_no_event():
    config = DataSourcesConfiguration(
        monthly_spending_paths=EventsDataPaths([]),
        one_time_spending_paths=EventsDataPaths([]),
        monthly_income_paths=EventsDataPaths([]),
        one_time_income_paths=EventsDataPaths([]),
    )
    scenario_config = ScenarioConfiguration(
        start_date=datetime.date(2023, 1, 1),
        end_date=datetime.date(2024, 1, 1),
    )
    event_log = EventGenerator(config=config).get_events(scenario_config)

    assert len(event_log) == 0


ScenarioExpectations = namedtuple("ScenarioExpectations", "scenario_config, n_expected_events")


_EXPECTATIONS_FOR_MONTHLY = (
    ScenarioExpectations(
        ScenarioConfiguration(
            start_date=datetime.date(1999, 1, 3),
            end_date=datetime.date(1999, 1, 5),
        ),
        0
    ),
    ScenarioExpectations(
        ScenarioConfiguration(
            start_date=datetime.date(2023, 1, 1),
            end_date=datetime.date(2023, 1, 1),
        ),
        1
    ),
    ScenarioExpectations(
        ScenarioConfiguration(
            start_date=datetime.date(2022, 12, 1),
            end_date=datetime.date(2022, 12, 1),
        ),
        2
    ),
    ScenarioExpectations(
        ScenarioConfiguration(
            start_date=datetime.date(2022, 12, 1),
            end_date=datetime.date(2023, 1, 1),
        ),
        3
    ),
    ScenarioExpectations(
        ScenarioConfiguration(
            start_date=datetime.date(2022, 1, 1),
            end_date=datetime.date(2022, 12, 30),
        ),
        8 + 12
    ),
    ScenarioExpectations(
        ScenarioConfiguration(
            start_date=datetime.date(2022, 1, 1),
            end_date=datetime.date(2022, 6, 5),
        ),
        6 + 2
    ),
)


@pytest.mark.parametrize("expectation", _EXPECTATIONS_FOR_MONTHLY)
def test_monthly_spending_produces_events(example_data_folder_path: str, expectation: ScenarioExpectations):
    data_config = DataSourcesConfiguration(
        monthly_spending_paths=EventsDataPaths(
            (os.path.join(example_data_folder_path, "first_of_the_month_event.csv"), )
        ),
        one_time_spending_paths=EventsDataPaths([]),
        monthly_income_paths=EventsDataPaths([]),
        one_time_income_paths=EventsDataPaths([]),
    )
    events = EventGenerator(config=data_config).get_events(expectation.scenario_config)
    assert len(events) == expectation.n_expected_events
    for e in events:
        assert expectation.scenario_config.start_date <= e.date <= expectation.scenario_config.end_date
        assert e.balance_impact < 0


@pytest.mark.parametrize("expectation", _EXPECTATIONS_FOR_MONTHLY)
def test_monthly_income_produces_events(
    example_data_folder_path: str, expectation: ScenarioExpectations
):
    date_config = DataSourcesConfiguration(
        monthly_spending_paths=EventsDataPaths([]),
        one_time_spending_paths=EventsDataPaths([]),
        monthly_income_paths=EventsDataPaths(
            (os.path.join(example_data_folder_path, "first_of_the_month_event.csv"), )
        ),
        one_time_income_paths=EventsDataPaths([]),
    )
    events = EventGenerator(config=date_config).get_events(expectation.scenario_config)
    assert len(events) == expectation.n_expected_events
    for e in events:
        assert expectation.scenario_config.start_date <= e.date <= expectation.scenario_config.end_date
        assert e.balance_impact > 0


def test_monthly_income_have_diferent_dates(example_data_folder_path: str):
    date_config = DataSourcesConfiguration(
        monthly_spending_paths=EventsDataPaths([]),
        one_time_spending_paths=EventsDataPaths([]),
        monthly_income_paths=EventsDataPaths(
            (os.path.join(example_data_folder_path, "first_of_the_month_event.csv"), )
        ),
        one_time_income_paths=EventsDataPaths([]),
    )
    scenario_config = ScenarioConfiguration(
        start_date=datetime.date(2003, 2, 2),
        end_date=datetime.date(2003, 4, 4),
    )
    events = EventGenerator(config=date_config).get_events(scenario_config)

    assert events[0].date == datetime.date(2003, 3, 1)
    assert events[1].date == datetime.date(2003, 4, 1)
    assert len(events) == 2


_EXPECTATIONS_FOR_ONE_TIME = (
    ScenarioExpectations(
        ScenarioConfiguration(
            start_date=datetime.date(1999, 1, 3),
            end_date=datetime.date(1999, 1, 5),
        ),
        0
    ),
    ScenarioExpectations(
        ScenarioConfiguration(
            start_date=datetime.date(2000, 1, 2),
            end_date=datetime.date(2000, 1, 2),
        ),
        1
    ),
    ScenarioExpectations(
        ScenarioConfiguration(
            start_date=datetime.date(1981, 1, 2),
            end_date=datetime.date(2100, 1, 2),
        ),
        1
    ),
    ScenarioExpectations(
        ScenarioConfiguration(
            start_date=datetime.date(2010, 1, 2),
            end_date=datetime.date(2011, 1, 2),
        ),
        0
    ),
)


@pytest.mark.parametrize("expectation", _EXPECTATIONS_FOR_ONE_TIME)
def test_one_time_income_produces_events(
    example_data_folder_path: str, expectation: ScenarioExpectations
):
    data_config = DataSourcesConfiguration(
        monthly_spending_paths=EventsDataPaths([]),
        one_time_spending_paths=EventsDataPaths([]),
        monthly_income_paths=EventsDataPaths([]),
        one_time_income_paths=EventsDataPaths(
            (os.path.join(example_data_folder_path, "one_time_event.csv"),),
        ),
    )
    events = EventGenerator(config=data_config).get_events(expectation.scenario_config)
    assert len(events) == expectation.n_expected_events
    for e in events:
        assert expectation.scenario_config.start_date <= e.date <= expectation.scenario_config.end_date
        assert e.balance_impact > 0


@pytest.mark.parametrize("expectation", _EXPECTATIONS_FOR_ONE_TIME)
def test_one_time_spending_produces_events(
    example_data_folder_path: str, expectation: ScenarioExpectations
):
    data_config = DataSourcesConfiguration(
        monthly_spending_paths=EventsDataPaths([]),
        one_time_spending_paths=EventsDataPaths(
            (os.path.join(example_data_folder_path, "one_time_event.csv"),),
        ),
        monthly_income_paths=EventsDataPaths([]),
        one_time_income_paths=EventsDataPaths([]),
    )
    events = EventGenerator(config=data_config).get_events(expectation.scenario_config)
    assert len(events) == expectation.n_expected_events
    for e in events:
        assert expectation.scenario_config.start_date <= e.date <= expectation.scenario_config.end_date
        assert e.balance_impact < 0


def test_events_are_sorted_by_date_ascending(example_data_folder_path: str):
    data_config = DataSourcesConfiguration(
        monthly_spending_paths=EventsDataPaths([]),
        one_time_spending_paths=EventsDataPaths(
            (os.path.join(example_data_folder_path, "one_time_event.csv"),),
        ),
        monthly_income_paths=EventsDataPaths(
            (os.path.join(example_data_folder_path, "first_of_the_month_event.csv"),),
        ),
        one_time_income_paths=EventsDataPaths([]),
    )
    scenario_config = ScenarioConfiguration(
        start_date=datetime.date(1981, 1, 2),
        end_date=datetime.date(2100, 1, 2),
    )

    events = EventGenerator(config=data_config).get_events(scenario_config)

    for idx, event in enumerate(events[:-1]):
        assert event.date <= events[idx + 1].date


def test_infinite_events(example_data_folder_path: str):
    data_config = DataSourcesConfiguration(
        monthly_spending_paths=EventsDataPaths((os.path.join(example_data_folder_path, "infinite_event.csv"),)),
        one_time_spending_paths=EventsDataPaths([]),
        monthly_income_paths=EventsDataPaths((os.path.join(example_data_folder_path, "infinite_event.csv"),)),
        one_time_income_paths=EventsDataPaths([]),
    )
    scenario_config = ScenarioConfiguration(
        start_date=datetime.date(2002, 8, 1),
        end_date=datetime.date(2002, 12, 1),
    )

    events = EventGenerator(config=data_config).get_events(scenario_config)

    assert len(events) == 10


def test_paid_one_time_events_are_skipped(example_data_folder_path: str):
    data_config = DataSourcesConfiguration(
        monthly_spending_paths=EventsDataPaths([]),
        one_time_spending_paths=EventsDataPaths((os.path.join(example_data_folder_path, "paid_events.csv"),)),
        monthly_income_paths=EventsDataPaths([]),
        one_time_income_paths=EventsDataPaths((os.path.join(example_data_folder_path, "paid_events.csv"),)),
    )
    scenario_config = ScenarioConfiguration(
        start_date=datetime.date(1998, 8, 1),
        end_date=datetime.date(2023, 12, 1),
    )

    events = EventGenerator(config=data_config).get_events(scenario_config)

    assert len(events) == 0
