import json
from typing import Any
from configmate.parsing import base_parser


class JsonParser(base_parser.BaseConfigParser):
    def _parse(self, data: str) -> Any:
        return json.loads(data)
