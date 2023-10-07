from collections import ChainMap
from configmate.aggregation import map_aggregators


def test_chain_map_aggregator():
    config1 = {"option1": "value1", "option2": "value2"}
    config2 = {"option2": "new_value2", "option3": "value3"}
    config3 = {"option3": "new_new_value3"}

    expected = ChainMap(config3, config2, config1)

    aggregator = map_aggregators.ChainMapAggregator()
    result = aggregator.aggregate(config1, config2, config3)

    assert result.maps == expected.maps
    assert result["option1"] == "value1"
    assert result["option2"] == "new_value2"
    assert result["option3"] == "new_new_value3"
