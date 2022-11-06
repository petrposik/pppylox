class LoxError(BaseException):
    pass


class LoxLexerError(LoxError):
    pass


class LoxParserError(LoxError):
    pass


def error_on(line: int, message: str) -> None:
    report(line, "", message)


def report(line: int, where: str, message: str) -> None:
    print(f"[line {line}] Error {where}: {message}")
