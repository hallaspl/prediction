import csv
from typing import List
import dataclasses as dc
from datetime import datetime

from pathlib import Path
from .types import Balance


class BalanceRepoException(Exception):
    ...


class DuplicateIdError(BalanceRepoException):
    ...


class UnknownIdError(BalanceRepoException):
    ...


@dc.dataclass(frozen=True)
class LogId:
    value: str


@dc.dataclass(frozen=True)
class BalanceLog:
    id: LogId
    balances: List[Balance]


class IBalanceRepo:
    def store_new_log(self, log: BalanceLog) -> None:
        raise NotImplementedError()

    def load_log(self, log_id: LogId) -> BalanceLog:
        raise NotImplementedError()


class CsvBalanceRepo(IBalanceRepo):
    def __init__(self, path: Path) -> None:
        self.__path = path
        self.__path.mkdir(exist_ok=True)

    def store_new_log(self, log: BalanceLog) -> None:
        try:
            self.__store_new_log(log)
        except FileExistsError as err:
            raise DuplicateIdError from err

    def __store_new_log(self, log: BalanceLog) -> None:
        new_file_path = self.__id_to_path(log.id)
        with open(new_file_path, "x") as file:
            writer = csv.writer(file)
            for balance in log.balances:
                to_write = dc.astuple(balance)
                writer.writerow(to_write)

    def load_log(self, log_id: LogId) -> BalanceLog:
        try:
            return self.__load_log(log_id)
        except FileNotFoundError as err:
            raise UnknownIdError from err

    def __load_log(self, log_id: LogId) -> BalanceLog:
        file_path = self.__id_to_path(log_id)
        balances = []
        with open(file_path) as file:
            reader = csv.reader(file)
            for row in reader:
                description = row[0]
                date = datetime.fromisoformat(row[1])
                value = int(row[2])
                balances.append(Balance(description, date, value))
        return BalanceLog(log_id, balances)

    def __id_to_path(self, log_id: LogId) -> Path:
        file_name = log_id.value + ".csv"
        return self.__path / file_name
