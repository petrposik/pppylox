class LoxError(BaseException):
    pass


class LoxLexerError(LoxError):
    pass


class LoxParserError(LoxError):
    pass
