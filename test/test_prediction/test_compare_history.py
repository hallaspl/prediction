import pytest
from typing import List
from datetime import date

from prediction.types import BalanceHistory, HistoryId, Balance, Difference
from prediction import HistoryComparator


def test_compareEmpty_noDifferences():
    history_id = HistoryId("nothin")
    first = BalanceHistory(history_id, [])
    second = BalanceHistory(history_id, [])
    comparator = HistoryComparator(first, second)

    result = comparator.compare()

    assert not result.diffs


def test_compareEmptyDifferentId_noDifferences():
    first = BalanceHistory(HistoryId("first"), [])
    second = BalanceHistory(HistoryId("second"), [])
    comparator = HistoryComparator(first, second)

    comparition = comparator.compare()

    assert not comparition.diffs


@pytest.mark.parametrize(
    "base_balances, compared_balances, desired",
    (
        pytest.param(
            [Balance("", date(2022, 2, 23), 5_000)],
            [Balance("", date(2022, 10, 9), 1_300)],
            [Difference(date(2022, 10, 9), -3_700)],
            id="base starts first, one compared"
        ),
        pytest.param(
            [Balance("", date(2022, 10, 9), 1_300)],
            [Balance("", date(2022, 2, 23), 5_000)],
            [Difference(date(2022, 10, 9), 3_700)],
            id="base starts later, one compared"
        ),
        pytest.param(
            [Balance("", date(2022, 2, 23), 5_000)],
            [
                Balance("", date(2022, 10, 9), 1_300),
                Balance("", date(2022, 10, 10), 4_300)
            ],
            [
                Difference(date(2022, 10, 9), -3_700),
                Difference(date(2022, 10, 10), -700)
            ],
            id="base starts first, two compared"
        ),
        pytest.param(
            [
                Balance("", date(2022, 10, 9), 1_300),
                Balance("", date(2022, 10, 10), 4_300)
            ],
            [Balance("", date(2022, 2, 23), 5_000)],
            [
                Difference(date(2022, 10, 9), 3_700),
                Difference(date(2022, 10, 10), 700)
            ],
            id="compared start first, one compared"
        ),
        pytest.param(
            [
                Balance("", date(2022, 2, 23), 5_000),
                Balance("", date(2022, 10, 11), 7_000)
            ],
            [
                Balance("", date(2022, 10, 1), 1_300),
                Balance("", date(2022, 10, 15), 4_300)
            ],
            [
                Difference(date(2022, 10, 1), -3_700),
                Difference(date(2022, 10, 11), -5_700),
                Difference(date(2022, 10, 15), -2_700)
            ],
            id="base starts first, alterating"
        ),
        pytest.param(
            [
                Balance("", date(2022, 10, 1), 1_300),
                Balance("", date(2022, 10, 15), 4_300)
            ],
            [
                Balance("", date(2022, 2, 23), 5_000),
                Balance("", date(2022, 10, 11), 7_000)
            ],
            [
                Difference(date(2022, 10, 1), 3_700),
                Difference(date(2022, 10, 11), 5_700),
                Difference(date(2022, 10, 15), 2_700)
            ],
            id="compared starts first, alterating"
        ),
        pytest.param(
            [
                Balance("", date(2022, 10, 1), 10),
                Balance("", date(2022, 10, 15), 40)
            ],
            [
                Balance("", date(2022, 2, 23), 1_000),
                Balance("", date(2022, 3, 11), 70)
            ],
            [
                Difference(date(2022, 10, 1), 60),
                Difference(date(2022, 10, 15), 30)
            ],
            id="compared starts first with two balances"
        ),
        pytest.param(
            [
                Balance("", date(2022, 2, 23), 5_000),
                Balance("", date(2022, 10, 11), 7_000),
            ],
            [
                Balance("", date(2022, 10, 1), 1_000),
                Balance("", date(2022, 10, 11), 10_000),
                Balance("", date(2022, 10, 15), 4_000),
            ],
            [
                Difference(date(2022, 10, 1), -4_000),
                Difference(date(2022, 10, 11), 3_000),
                Difference(date(2022, 10, 15), -3_000),
            ],
            id="same date compared"
        ),
        pytest.param(
            [
                Balance("", date(2022, 10, 1), 1_000),
                Balance("", date(2022, 10, 11), 10_000),
                Balance("", date(2022, 10, 15), 4_000),
            ],
            [
                Balance("", date(2022, 2, 23), 5_000),
                Balance("", date(2022, 10, 11), 7_000),
            ],
            [
                Difference(date(2022, 10, 1), 4_000),
                Difference(date(2022, 10, 11), -3_000),
                Difference(date(2022, 10, 15), 3_000),
            ],
            id="same date reversed"
        ),
        pytest.param(
            [Balance("", date(2022, 10, 11), 1_300)],
            [Balance("", date(2022, 2, 23), 5_000)],
            [Difference(date(2022, 10, 11), 3_700)],
            id="one compared starts first"
        ),
        pytest.param(
            [Balance("", date(2022, 10, 11), 1_000)],
            [
                Balance("", date(2022, 2, 23), 5_000),
                Balance("", date(2022, 3, 23), 8_000),
            ],
            [Difference(date(2022, 10, 11), 7_000)],
            id="many compared starts first"
        ),
        pytest.param(
            [Balance("", date(2022, 10, 11), 1_000)],
            [
                Balance("", date(2022, 2, 23), 5_000),
                Balance("", date(2022, 3, 23), 6_000),
                Balance("", date(2022, 10, 11), 8_000),
            ],
            [Difference(date(2022, 10, 11), 7_000)],
            id="many past balances, date equal"
        ),
        # pytest.param(
        #     [
        #         Balance("", date(2022, 10, 11), 1_000),
        #         Balance("", date(2022, 11, 11), 1_000),
        #         Balance("", date(2022, 12, 11), 1_000),
        #     ],
        #     [
        #         Balance("", date(2022, 2, 23), 5_000),
        #         Balance("", date(2022, 3, 23), 6_000),
        #         Balance("", date(2022, 10, 11), 8_000),
        #     ],
        #     [Difference(date(2022, 10, 11), 7_000)],
        #     id="many past balances, date equal"
        # ),
    )
)
def test_compare(
    base_balances: List[Balance],
    compared_balances: List[Balance],
    desired: List[Difference]
):
    history_id = HistoryId("nothin")
    base = BalanceHistory(history_id, base_balances)
    compared = BalanceHistory(history_id, compared_balances)
    comparator = HistoryComparator(base, compared)

    result = comparator.compare()

    for diff in desired:
        assert diff in result.diffs
    assert result.diffs == desired
