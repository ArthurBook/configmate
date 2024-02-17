import pytest
from configmate.base import exceptions
from configmate.components import aggregators


def test_function_aggregator_aggregate_with_function():
    # Test that FunctionAggregator correctly applies a function over an iterable
    aggregator = aggregators.FunctionAggregator(sum)
    assert aggregator([1, 2, 3]) == 6


@pytest.mark.parametrize(
    "input_data,expected_output",
    [
        ([[1, 2], [3, 4]], [1, 2, 3, 4]),
        ([], []),
    ],
)
def test_inferred_aggregator_aggregate_sequences(
    input_data: list[list[int]], expected_output: list[int]
):
    aggregator = aggregators.InferredAggregator()
    assert aggregator(input_data) == expected_output


@pytest.mark.parametrize(
    "input_data,expected_output",
    [
        ([{"a": 1}, {"b": 2}], {"a": 1, "b": 2}),
        ([{}], {}),
    ],
)
def test_inferred_aggregator_aggregate_mappings(
    input_data: list[dict], expected_output: dict
) -> None:
    aggregator = aggregators.InferredAggregator()
    assert aggregator(input_data) == expected_output


def test_inferred_aggregator_aggregate_mixed_types() -> None:
    aggregator = aggregators.InferredAggregator()
    with pytest.raises(exceptions.AggregationFailure):
        aggregator([1, "a"])


def test_aggregator_factory_build_function_aggregator():
    aggregator = aggregators.AggregatorFactory.build_aggregator(sum)
    assert isinstance(aggregator, aggregators.FunctionAggregator)


def test_aggregator_factory_build_inferred_aggregator_for_any_spec():
    aggregator = aggregators.AggregatorFactory.build_aggregator(None)
    assert isinstance(aggregator, aggregators.InferredAggregator)


if __name__ == "__main__":
    pytest.main()
