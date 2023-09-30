class CommandLineReadingError(Exception):
    """Raised when a command line argument cannot be read."""


class NeedsExtension(Exception):
    """Raised when a parser needs an extension to work."""


class UnfilledEnvironmentVariableError(Exception):
    """Raised when an environment variable is not set."""
