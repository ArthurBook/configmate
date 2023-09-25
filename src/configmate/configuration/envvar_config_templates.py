import re
from configmate.configuration import configuration_base

UNIX_ENV_PATTERN = re.compile(r"^(?![#/])\$(\w+|\{[^}]*\})")
WINDOWS_ENV_PATTERN = re.compile(r"^(?![#/])%([A-Za-z0-9_]+)%", re.IGNORECASE)

DEFAULT = configuration_base.EnvironmentVariableHandlingConfig(
    env_var_pattern=UNIX_ENV_PATTERN,
    defaults={},
    handling=configuration_base.EnvVarMode.RAISE_MISSING,
)
