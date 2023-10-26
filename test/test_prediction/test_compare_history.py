import pytest

from prediction.types import Balance, BalanceHistory, HistoryId
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


def test_comparitionStartsAtCommonDate():
    pass
