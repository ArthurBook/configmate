class CommandLineReadingError(Exception):
    """Raised when a command line argument cannot be read."""


class UnfilledEnvironmentVariableError(Exception):
    """Raised when an environment variable is not set."""
