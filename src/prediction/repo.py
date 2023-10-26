import csv
import dataclasses as dc
from datetime import datetime

from pathlib import Path
from prediction.types import Balance, BalanceHistory, HistoryId
from prediction.interface import IBalanceRepo


class BalanceRepoException(Exception):
    ...


class DuplicateIdError(BalanceRepoException):
    ...


class UnknownIdError(BalanceRepoException):
    ...


class CsvBalanceRepo(IBalanceRepo):
    def __init__(self, path: Path) -> None:
        self.__path = path
        self.__path.mkdir(exist_ok=True)

    def store_new_history(self, history: BalanceHistory) -> None:
        try:
            self.__store_new_history(history)
        except FileExistsError as err:
            raise DuplicateIdError from err

    def __store_new_history(self, history: BalanceHistory) -> None:
        new_file_path = self.__id_to_path(history.id)
        with open(new_file_path, "x") as file:
            writer = csv.writer(file)
            for balance in history.balances:
                to_write = dc.astuple(balance)
                writer.writerow(to_write)

    def load_history(self, history_id: HistoryId) -> BalanceHistory:
        try:
            return self.__load_history(history_id)
        except FileNotFoundError as err:
            raise UnknownIdError from err

    def __load_history(self, log_id: HistoryId) -> BalanceHistory:
        file_path = self.__id_to_path(log_id)
        balances = []
        with open(file_path) as file:
            reader = csv.reader(file)
            for row in reader:
                description = row[0]
                date = datetime.fromisoformat(row[1])
                value = int(row[2])
                balances.append(Balance(description, date, value))
        return BalanceHistory(log_id, balances)

    def __id_to_path(self, history_id: HistoryId) -> Path:
        file_name = history_id.value + ".csv"
        return self.__path / file_name
