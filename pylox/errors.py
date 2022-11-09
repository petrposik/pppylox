class LoxError(BaseException):
    pass


class LoxLexerError(LoxError):
    pass


class LoxParserError(LoxError):
    pass


class LoxRuntimeError(LoxError):
    def __init__(self, token, *args):
        super().__init__(*args)
        self.token = token

    def __str__(self):
        return super().__str__()
