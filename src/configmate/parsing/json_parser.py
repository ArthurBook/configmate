import json
from typing import Any, Set
from configmate.parsing import base_parser


class JsonParser(base_parser.InferableConfigParser):
    def _parse(self, data: str) -> Any:
        return json.loads(data)

    @classmethod
    def supported_file_extensions(cls) -> Set[str]:
        return {".json"}
