import os
from typing import Any, Dict, List
from unittest import mock

import pytest

from configmate import get_config

TEST_FILE_FOLDER = "./tests/test_files/"
BASE_FILE = "test.json"
OVERRIDE_FILE = "test_override.json"


@pytest.mark.parametrize(
    "files, env, target",
    [
        (
            [os.path.join(TEST_FILE_FOLDER, BASE_FILE)],
            {},
            {
                "foo": "bar",
                "hax": "ban",  # from JSON
            },
        ),
        (
            [
                os.path.join(TEST_FILE_FOLDER, BASE_FILE),
                os.path.join(TEST_FILE_FOLDER, OVERRIDE_FILE),  # overrides JSON
            ],
            {},  # BAN defaults to 2
            {
                "foo": "bar",
                "hax": 2,
            },
        ),
        (
            [
                os.path.join(TEST_FILE_FOLDER, BASE_FILE),
                os.path.join(TEST_FILE_FOLDER, OVERRIDE_FILE),  # overrides JSON
            ],
            {
                "BAN": "1",  # taken from ENV
            },
            {
                "foo": "bar",
                "hax": 1,
            },
        ),
    ],
)
def test_end_to_end(files: List[str], env: Dict[str, str], target: Any) -> None:
    with mock.patch.dict(os.environ, env, clear=True):
        config: Dict[Any, Any] = get_config(*files, validation=dict)
        assert config == target, f"Expected {target}, got {config}"


if __name__ == "__main__":
    pytest.main()
