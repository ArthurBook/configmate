class ConfigmateError(Exception):
    """Base class for all configmate errors."""


class NoStrategyAvailable(ConfigmateError):
    """Raised when no overlay strategy is applicable"""


class SectionNotFound(ConfigmateError):
    """Raised when the specified section is not found."""


class UnfilledEnvironmentVariableError(ConfigmateError):
    """Raised when an environment variable is not set."""


class InvalidConfigError(ConfigmateError):
    """Raised when a config is invalid."""
