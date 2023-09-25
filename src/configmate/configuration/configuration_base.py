import enum
import dataclasses
import os
import re
from typing import Dict, Union


### Configuration ###
@dataclasses.dataclass
class SourceConfig:
    path: Union[str, os.PathLike]
    encoding: str = "utf-8"


### Environment variable handling ###
class EnvVarMode(str, enum.Enum):
    """
    Options for handling unfilled environment variables.
    """

    RAISE_MISSING = "raise_missing"
    LOG_MISSING = "log_missing"
    WARN_MISSING = "warn_missing"
    IGNORE_MISSING = "ignore_missing"
    FILL_WITH_BLANK = "fill_blank"


@dataclasses.dataclass
class EnvironmentVariableHandlingConfig:
    """
    Configuration for how to handle environment variables.
    """

    handling: EnvVarMode
    env_var_pattern: re.Pattern
    defaults: Dict[str, str] = dataclasses.field(default_factory=dict)


### Parsing configuration ###
class SupportedParsers(str, enum.Enum):
    """
    Enum of supported parsers.
    """

    INFER = "infer"
    COMMANDLINE = "commandline"
    JSON = "json"
    TOML = "toml"
    INI = "ini"
    YAML_SAFE_LOAD = "yaml_safe_load"
    YAML_UNSAFE_LOAD = "yaml_unsafe_load"
    EVAL = "eval"


@dataclasses.dataclass
class ParsingConfig:
    parser_type: SupportedParsers = SupportedParsers.INFER
