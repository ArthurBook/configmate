""" Components for config pipelines
"""

from configmate.components.aggregators import (
    AggregationSpec,
    AggregatorFactory,
    FunctionAggregator,
    InferredAggregator,
)
from configmate.components.cli_readers import (
    ArgSelector,
    CliSectionReader,
    KeyValueSelector,
)
from configmate.components.interpolators import (
    FunctionalInterpolator,
    InterpolatorChain,
    InterpolatorFactory,
    InterpolatorSpec,
    VariableInterpolator,
)
from configmate.components.parsers import (
    FileFormatParserRegistry,
    FunctionParser,
    InferredParser,
    IniParser,
    JsonParser,
    ParserFactory,
    ParsingSpec,
    XmlParser,
)
from configmate.components.selectors import (
    SectionSelectionSpec,
    SectionSelector,
    SectionSelectorFactory,
)
from configmate.components.validators import (
    FunctionValidator,
    TypeValidatorFactory,
    ValidationSpec,
)

__all__ = [
    ## cli_readers
    "ArgSelector",
    "CliSectionReader",
    "KeyValueSelector",
    ## aggregators
    "AggregationSpec",
    "AggregatorFactory",
    "FunctionAggregator",
    "InferredAggregator",
    ## interpolators
    "FunctionalInterpolator",
    "InterpolatorChain",
    "InterpolatorFactory",
    "InterpolatorSpec",
    "VariableInterpolator",
    ## parsers
    "FileFormatParserRegistry",
    "FunctionParser",
    "InferredParser",
    "IniParser",
    "JsonParser",
    "ParserFactory",
    "ParsingSpec",
    "XmlParser",
    ## selectors
    "SectionSelectionSpec",
    "SectionSelector",
    "SectionSelectorFactory",
    "ValidationSpec",
    "FunctionValidator",
    "TypeValidatorFactory",
]
