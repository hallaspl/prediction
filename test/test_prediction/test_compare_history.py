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


def test_compareEmtryDifferentId_noDifferences():
    first = BalanceHistory(HistoryId("first"), [])
    second = BalanceHistory(HistoryId("second"), [])
    comparator = HistoryComparator(first, second)

    comparition = comparator.compare()

    assert not comparition.diffs


@pytest.mark.parametrize(
    "base_balances, compared_balances, desired",
    (
        # pytest.param(
        #     [Balance("", date(2022, 10, 11), 1_300)],
        #     [Balance("", date(2022, 2, 23), 5_000)],
        #     [Difference(date(2022, 10, 11), 3_700)],
        #     id="compared starts first"
        # ),
        pytest.param(
            [Balance("", date(2022, 2, 23), 5_000)],
            [Balance("", date(2022, 10, 9), 1_300)],
            [Difference(date(2022, 10, 9), -3_700)],
            id="base starts first, one compared"
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
    assert len(result.diffs) == len(desired)
    assert result.diffs == desired
