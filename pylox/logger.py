# print("pylox/logger.py")

import logging
from rich.logging import RichHandler

logger = logging.getLogger(__name__)

# The handler determines where the log messages go: stdout/file
# shell_handler = logging.StreamHandler()
shell_handler = RichHandler(rich_tracebacks=True)
file_handler = logging.FileHandler("debug.log")

logger.setLevel(logging.DEBUG)
shell_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

# The formatter determines how the log messages are formatted
# fmt_shell = '%(asctime)s %(levelname)s %(message)s'
fmt_shell = "%(message)s"
fmt_file = (
    "%(asctime)s %(levelname)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s"
)
shell_formater = logging.Formatter(fmt_shell)
file_formatter = logging.Formatter(fmt_file)
shell_handler.setFormatter(shell_formater)
file_handler.setFormatter(file_formatter)

# Shell handler is added only in run scripts, perhaps after specifying a command line argument -l
# logger.addHandler(shell_handler)
logger.addHandler(file_handler)
