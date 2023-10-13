import collections
from typing import Any, ChainMap, Mapping

from configmate.aggregation import base_aggregator


class ChainMapAggregator(base_aggregator.MapAggregator):
    def aggregate(self, *configs: Mapping[str, Any]) -> ChainMap[str, Any]:
        config_dicts = (dict(config) for config in configs)
        config_chainmap = collections.ChainMap(*config_dicts)
        config_chainmap.maps.reverse()
        return config_chainmap
