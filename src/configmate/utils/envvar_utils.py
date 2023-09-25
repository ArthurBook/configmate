import collections
import logging
import os
import re
import warnings
from typing import Iterable, Mapping, Optional, Set

from configmate import exceptions
from configmate.configuration import configuration_base

logger = logging.getLogger(__name__)


def replace_env_variables(
    string: str,
    config: configuration_base.EnvironmentVariableHandlingConfig,
) -> str:
    """
    Replace environment variables in a string with their values.
    """
    fill_vals = collections.ChainMap(os.environ, config.defaults)
    unfilled_vars: Set[str] = set()

    def replacer(match: re.Match) -> str:
        nonlocal unfilled_vars
        if (fill_val := get_env_var_value(match, fill_vals, config.handling)) is None:
            unfilled_vars.add(match.group(0))
        return fill_val or ""

    filled_var_string = config.env_var_pattern.sub(replacer, string)
    if unfilled_vars:
        handle_unfilled_variables(unfilled_vars, config)

    return filled_var_string


def get_env_var_value(
    match: re.Match,
    fill_value_map: Mapping[str, str],
    handling_mode: configuration_base.EnvVarMode,
) -> Optional[str]:
    """
    Get the value of an environment variable.
    """
    variable_name = get_variable_name_from_match(match)
    if (fill_val := fill_value_map.get(variable_name)) is not None:
        return fill_val
    if handling_mode is configuration_base.EnvVarMode.IGNORE_MISSING:
        return match.group(0)
    if handling_mode is configuration_base.EnvVarMode.FILL_WITH_BLANK:
        return ""
    return None


def get_variable_name_from_match(match: re.Match) -> str:
    assert match.lastindex is not None
    for i in range(1, match.lastindex + 1):
        var_name: Optional[str] = match.group(i)
        if var_name is not None:
            return var_name
    assert False, "Should not reach this point"


def handle_unfilled_variables(
    unfilled_vars: Iterable[str],
    config: configuration_base.EnvironmentVariableHandlingConfig,
) -> None:
    if config.handling is configuration_base.EnvVarMode.RAISE_MISSING:
        raise exceptions.UnfilledEnvironmentVariableError(unfilled_vars)
    if config.handling is configuration_base.EnvVarMode.LOG_MISSING:
        logger.warn(f"Following environment variables not found: {unfilled_vars}")
    if config.handling is configuration_base.EnvVarMode.WARN_MISSING:
        warnings.warn(f"Following environment variables not found: {unfilled_vars}")
