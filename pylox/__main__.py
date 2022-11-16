# print("pylox/__main__.py")

import sys
import pylox
from .pylox import Lox
from .repl import LoxREPL


def main():
    if len(sys.argv) > 1:
        Lox().run_file(sys.argv[1])
    else:
        LoxREPL().cmdloop()


main()
