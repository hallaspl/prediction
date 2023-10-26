import pytest
from typing import List
from datetime import datetime
from pathlib import Path
from prediction.repo import CsvBalanceRepo, IBalanceRepo, HistoryId, BalanceHistory, DuplicateIdError, UnknownIdError
from prediction import Balance


@pytest.fixture
def example_log() -> List[Balance]:
    log = [
        Balance("some notes", datetime.now(), 12213),
        Balance("Additional notes", datetime.now(), 444)
    ]
    log_id = HistoryId("121314")
    return BalanceHistory(log_id, log)


@pytest.fixture
def repo_path(tmp_path: Path) -> Path:
    return tmp_path / "csv_repo"


@pytest.fixture
def repo(repo_path: Path) -> IBalanceRepo:
    return CsvBalanceRepo(repo_path)


def test_dirDoseNotExist_dirIsCreated(
    repo_path: Path, repo: IBalanceRepo
):
    assert repo_path.exists()


def test_store_newFileCreated(
    repo_path: Path, repo: IBalanceRepo, example_log: BalanceHistory
):
    expected_file_path = repo_path / (example_log.id.value + ".csv")

    repo.store_new_history(example_log)

    assert expected_file_path.exists()
    assert expected_file_path.is_file()


def test_storeLoad_logsAreEqual(
    repo: IBalanceRepo, example_log: BalanceHistory
):
    repo.store_new_history(example_log)
    log = repo.load_history(example_log.id)
    assert log == example_log


def test_storeStore_raise(repo: IBalanceRepo, example_log: BalanceHistory):
    repo.store_new_history(example_log)
    with pytest.raises(DuplicateIdError):
        repo.store_new_history(example_log)


def test_load_raise(repo: IBalanceRepo):
    with pytest.raises(UnknownIdError):
        repo.load_history(HistoryId("whatever"))
