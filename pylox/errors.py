class LoxError(BaseException):
    pass


class LoxLexerError(LoxError):
    pass


class LoxParserError(LoxError):
    pass


class LoxRuntimeError(LoxError):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token


def error_on(line: int, message: str) -> None:
    report(line, "", message)


def report(line: int, where: str, message: str) -> None:
    print(f"[line {line}] Error {where}: {message}")
