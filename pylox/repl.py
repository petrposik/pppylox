# print("pylox/repl.py")

import cmd
from io import StringIO

from .pylox import Lox
from .lexer import Lexer


class LoxREPL(cmd.Cmd):
    intro = "Welcome to Lox REPL.\nType help or ? to list commands."
    prompt = "\nlox> "
    lox = Lox()

    # Tried the autocompletion, but it does not work.
    # After hitting <Tab>, the cursor moves ahead instead of offering completions
    # def completedefault(self, text, line, begidx, endidx):
    #     return [''.join(text, *random.choices('abcdefghijklmnopqrstuvwxyz', k=3)) for _ in range(5)]

    def do_lexer(self, arg: str) -> bool:
        "Enter Lox lexer testing mode. Write strings and see tokens produced by Lox lexer."
        LexerREPL().cmdloop()
        return False

    # def do_parser(self, arg: str) -> bool:
    #     "Enter Lox parser testing mode. Write strings and see results produced by Lox parser."
    #     ParserREPL().cmdloop()
    #     return False

    def do_reset(self, arg: str) -> bool:
        "Reset the Lox interpreter"
        self.lox = Lox()
        return False

    def do_quit(self, arg):
        "Quit Lox:  QUIT"
        print("Thank you for using Lox REPL.")
        return True

    def do_exec(self, arg):
        "Load the Lox source from file and execute it"
        try:
            self.lox.exec(arg)
        except Exception as e:
            print(f"ERROR: Execution of {arg} failed:")
            print(e.message)

    def default(self, line):
        if line == "EOF":
            return True
        self.lox.exec_line(line)


class LexerREPL(cmd.Cmd):
    intro = "Entering Lox lexer. Enter strings and see how Lox lexer tokenizes them."
    prompt = "\nlox lexer> "

    def do_quit(self, arg):
        print("Leaving Lox lexer.")
        return True

    def default(self, arg):
        lexer = Lexer(StringIO(arg))
        tokens = list(lexer)
        for token in tokens:
            print(token)
        return False
