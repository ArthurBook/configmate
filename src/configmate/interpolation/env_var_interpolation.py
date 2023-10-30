"""
Environment variable interpolation.
"""
import collections
import enum
import os
import re
import warnings
from typing import Collection, Dict, Iterable, Mapping, Optional, Set, Union

from configmate import base, commons, exceptions
from configmate.interpolation import interpolator_factory as factory

DEFAULT_ENV_VAR_PATTERN = UNIX_ENV_PATTERN = re.compile(r"^(?![#/])\$(\w+|\{[^}]*\})")
WINDOWS_ENV_PATTERN = re.compile(r"^(?![#/])%([A-Za-z0-9]+)%", re.IGNORECASE)


class MissingPolicy(str, enum.Enum):
    """Options for handling unfilled environment variables."""

    RAISE_EXCEPTION = "raise_missing"
    WARN = "warn_missing"
    IGNORE = "ignore_missing"


@factory.InterpFactoryRegistry.register(commons.make_typechecker(MissingPolicy))
class EnvInterpolator(base.BaseInterpolator):
    def __init__(
        self,
        handling: MissingPolicy = MissingPolicy.WARN,
        env_var_pattern: re.Pattern = DEFAULT_ENV_VAR_PATTERN,
        defaults: Optional[Dict[str, str]] = None,
        ignore_vars: Collection[Union[str, re.Pattern]] = (),
    ) -> None:
        super().__init__()
        self.pattern = env_var_pattern
        self.mode = handling
        self.defaults = defaults
        self.ignore_vars = ignore_vars

    def interpolate(self, text: str) -> str:
        return expand_env_vars(
            string=text,
            env_var_pattern=self.pattern,
            missing_behaviour=self.mode,
            defaults=self.defaults,
            ignore_vars=self.ignore_vars,
        )


def expand_env_vars(
    string: str,
    env_var_pattern: re.Pattern = DEFAULT_ENV_VAR_PATTERN,
    missing_behaviour: MissingPolicy = MissingPolicy.WARN,
    defaults: Optional[Dict[str, str]] = None,
    ignore_vars: Collection[Union[str, re.Pattern]] = (),
) -> str:
    fill_vals = collections.ChainMap(os.environ, defaults or {})
    unfilled_vars: Set[str] = set()

    def replacer(match: re.Match) -> str:
        nonlocal unfilled_vars
        if should_be_ignored(env_var_name := match.group(0), ignore_vars):
            return match.group(0)
        if (fill_val := get_env_var_value(match, fill_vals, missing_behaviour)) is None:
            unfilled_vars.add(env_var_name)
        return fill_val or ""

    filled_var_string = env_var_pattern.sub(replacer, string)
    if unfilled_vars:
        handle_unfilled_vars(unfilled_vars, missing_behaviour)

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
        if isinstance(ignore_item, re.Pattern) and ignore_item.search(variable_name):
            return True
    return False


def get_env_var_value(
    match: re.Match,
    fill_value_map: Mapping[str, str],
    handling_mode: MissingPolicy,
) -> Optional[str]:
    """
    Get the value of an environment variable.
    """
    variable_name = get_variable_name_from_match(match)
    if (fill_val := fill_value_map.get(variable_name)) is not None:
        return fill_val
    if handling_mode is MissingPolicy.IGNORE:
        return match.group(0)
    return None


def get_variable_name_from_match(match: re.Match) -> str:
    assert match.lastindex is not None
    for idx in range(1, match.lastindex + 1):
        var_name: Optional[str] = match.group(idx)
        if var_name is not None:
            return var_name
    assert False, "Should not reach this point"


def handle_unfilled_vars(
    unfilled_vars: Iterable[str], handling_mode: MissingPolicy
) -> None:
    if handling_mode is MissingPolicy.RAISE_EXCEPTION:
        raise exceptions.UnfilledEnvironmentVariableError(unfilled_vars)
    if handling_mode is MissingPolicy.WARN:
        warnings.warn(f"Following environment variables not found: {unfilled_vars}")
    raise NotImplementedError(f"Handling mode {handling_mode} is not implemented yet.")
