"""This module contains all the exceptions that are raised by configmate."""


class ConfigmateError(Exception):
    "Base class for all configmate errors."


class NoApplicableStrategy(ConfigmateError):
    "Raised when no strategy is applicable."


class SectionNotFound(ConfigmateError):
    "Raised when the specified section is not found."


class MissingEnvironmentVariable(ConfigmateError):
    "Raised for missing environment variables."


class AggregationFailure(ConfigmateError):
    "Raised when aggregation fails."
