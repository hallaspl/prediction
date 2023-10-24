class BalanceException(Exception):
    pass


class ValidationError(BalanceException):
    pass


class CalculatorError(BalanceException):
    pass
