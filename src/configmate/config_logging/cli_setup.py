import argparse
import datetime as dt
import logging
import os
from typing import Union
from configmate.config_logging import configmate_logger
from configmate import cli

logger = configmate_logger.logger

DEFAULT_LOG_DIR = f"logs/{dt.datetime.now(dt.timezone.utc).isoformat()}-configmate.log"

# Map CLI verbosity to logging levels
VERBOSITY_LEVEL_MAP = {
    0: configmate_logger.LoggingLevels.WARNING,  # default
    1: configmate_logger.LoggingLevels.INFO,  # -v
    2: configmate_logger.LoggingLevels.DEBUG,  # -vv
    3: configmate_logger.LoggingLevels.TRACE,  # -vvv
}


# Initialize argparse
cli.configmate_cliparser.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    help="Set configmate verbosity level (between -v and -vvv)",
)

cli.configmate_cliparser.add_argument(
    "--logfile",
    type=str,
    nargs="?",  # zero or one argument
    const=DEFAULT_LOG_DIR,
    default="",
    help=f'Log file path. If no path is given, defaults to "{DEFAULT_LOG_DIR}',
)


def set_config_from_arg_argparser(log_argparser: argparse.ArgumentParser) -> None:
    parsed_args = log_argparser.parse_args()
    set_verbosity_level(parsed_args.verbose)
    set_log_dir(parsed_args.logfile)


def set_verbosity_level(level: int) -> None:
    if level == 0:
        return
    if level > 3:
        logger.warning("Got verbosity=%i setting verbosity level to 3", level)
        level = 3
    verbosity = VERBOSITY_LEVEL_MAP[level]
    logger.setLevel(verbosity)


def set_log_dir(log_file: Union[str, os.PathLike]) -> None:
    if not log_file:
        return
    if not os.path.exists(log_file):
        os.makedirs(log_file)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(configmate_logger.formatter)
    logger.addHandler(file_handler)
