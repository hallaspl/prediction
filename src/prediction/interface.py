from prediction.types import HistoryId, BalanceHistory


class IBalanceRepo:
    def store_new_history(self, history: BalanceHistory) -> None:
        raise NotImplementedError()

    def load_history(self, history_id: HistoryId) -> BalanceHistory:
        raise NotImplementedError()
