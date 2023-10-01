import collections
import os
import re
import warnings
from typing import Iterable, Mapping, Optional, Set, Union, cast

from configmate import exceptions
from configmate.configuration import envvar_config
from configmate.interpolation import base_interpolator
from configmate.utils import configmate_logger

logger = configmate_logger.logger.getChild(__name__)


class EnvVarInterpolator(base_interpolator.BaseInterpolator):
    def __init__(self, config: envvar_config.EnvVarConfig) -> None:
        super().__init__()
        self.config = config

    def interpolate_content(self, string: str) -> str:
        return fill_env_variables(string, self.config)


def fill_env_variables(string: str, config: envvar_config.EnvVarConfig) -> str:
    """
    Replace environment variables in a string with their values.

    Args:
        string: The string to replace environment variables in.
        config: The configuration for how to fill environment variables.

    Returns:
        The string with replaced environment variables.
    """

    fill_vals = collections.ChainMap(os.environ, config.defaults)  # type: ignore
    unfilled_vars: Set[str] = set()

    def replacer(match: re.Match) -> str:
        nonlocal unfilled_vars
        if should_be_ignored(env_var_name := match.group(0), config.ignore):
            return match.group(0)
        if (fill_val := get_env_var_value(match, fill_vals, config.handling)) is None:
            unfilled_vars.add(env_var_name)
        return str(fill_val) or ""

    filled_var_string = config.env_var_pattern.sub(replacer, string)
    if unfilled_vars:
        handle_unfilled_variables(unfilled_vars, config.handling)

    return filled_var_string


def should_be_ignored(
    variable_name: str,
    ignore_vars: Iterable[Union[str, re.Pattern]],
) -> bool:
    """
    Check if a variable should be ignored.
    """
    for ignore_item in ignore_vars:
        if isinstance(ignore_item, str) and variable_name == ignore_item:
            return True
        if cast(re.Pattern, ignore_item).search(variable_name):
            return True
    return False


def get_env_var_value(
    match: re.Match,
    fill_value_map: Mapping[str, envvar_config.CanBeStringed],
    handling_mode: envvar_config.EnvVarMode,
) -> Optional[envvar_config.CanBeStringed]:
    """
    Get the value of an environment variable.
    """
    variable_name = get_variable_name_from_match(match)
    if (fill_val := fill_value_map.get(variable_name)) is not None:
        return fill_val
    if handling_mode is envvar_config.EnvVarMode.IGNORE_MISSING:
        return match.group(0)
    if handling_mode is envvar_config.EnvVarMode.FILL_WITH_BLANK:
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
    handling_mode: envvar_config.EnvVarMode,
) -> None:
    if handling_mode is envvar_config.EnvVarMode.RAISE_MISSING:
        raise exceptions.UnfilledEnvironmentVariableError(unfilled_vars)
    if handling_mode is envvar_config.EnvVarMode.LOG_MISSING:
        logger.warning("Following environment variables not found: %s", unfilled_vars)
    if handling_mode is envvar_config.EnvVarMode.WARN_MISSING:
        warnings.warn(f"Following environment variables not found: {unfilled_vars}")
    raise NotImplementedError(f"Handling mode {handling_mode} is not implemented yet.")
