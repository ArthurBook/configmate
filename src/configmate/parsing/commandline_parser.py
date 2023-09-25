import argparse

from configmate.parsing import parser_base


class CommandLineReader(parser_base.ConfigParser):
    def __init__(self) -> None:
        super().__init__()
        self.parser = argparse.ArgumentParser()

    def _read_config(self) -> str:
        _, args = self.parser.parse_known_args()
        return " ".join(args)
