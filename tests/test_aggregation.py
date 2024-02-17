import pytest
from configmate.base import exceptions, operators
from configmate.components import aggregators


@pytest.fixture
def context() -> operators.Context:
    return operators.Context()


def test_function_aggregator_aggregate_with_function(context: operators.Context):
    # Test that FunctionAggregator correctly applies a function over an iterable
    func = sum
    aggregator = aggregators.FunctionAggregator(func)
    assert aggregator._transform(context, [1, 2, 3]) == 6


@pytest.mark.parametrize(
    "input_data,expected_output",
    [
        ([[1, 2], [3, 4]], [1, 2, 3, 4]),
        ([], []),
    ],
)
def test_inferred_aggregator_aggregate_sequences(
    input_data: list[list[int]], expected_output: list[int], context: operators.Context
):
    aggregator = aggregators.InferredAggregator()
    assert aggregator._transform(context, input_data) == expected_output


@pytest.mark.parametrize(
    "input_data,expected_output",
    [
        ([{"a": 1}, {"b": 2}], {"a": 1, "b": 2}),
        ([{}], {}),
    ],
)
def test_inferred_aggregator_aggregate_mappings(
    input_data: list[dict], expected_output: dict, context: operators.Context
) -> None:
    aggregator = aggregators.InferredAggregator()
    assert aggregator._transform(context, input_data) == expected_output


def test_inferred_aggregator_aggregate_mixed_types(context: operators.Context) -> None:
    aggregator = aggregators.InferredAggregator()
    with pytest.raises(exceptions.AggregationFailure):
        aggregator._transform(context, [1, "a"])


def test_aggregator_factory_build_function_aggregator():
    aggregator = aggregators.AggregatorFactory.build_aggregator(sum)
    assert isinstance(aggregator, aggregators.FunctionAggregator)


def test_aggregator_factory_build_inferred_aggregator_for_any_spec():
    aggregator = aggregators.AggregatorFactory.build_aggregator(None)
    assert isinstance(aggregator, aggregators.InferredAggregator)


if __name__ == "__main__":
    pytest.main()
