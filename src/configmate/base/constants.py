import json
import os
import re
import sys
import types
from typing import Literal
from configmate.base import types as configmate_types

SYS_DEFAULT_FILE_ENCODING = sys.getdefaultencoding()

CLI_OVERLAY_FILE_PREFIX = "+"
CLI_OVERLAY_KWARG_KEY_PREFIX = "++"
CLI_OVERLAY_KWARG_KEY_DELIMITER = "."
CLI_OVERLAY_KWARG_VAL_PARSER = json.loads
CLI_SECTION_END_TOKEN = "/"

CLI_ARGS = sys.argv
ENVIRONMENT = types.MappingProxyType(os.environ)  # read-only view of the env-vars
BASH_VAR_PATTERN = re.compile(r"\${(?P<variable>\w+)(?::(?P<default_value>[^}:]+))?}")

OVERLAY: Literal["overlay"] = "overlay"

INFER_FROM_PATH = configmate_types.Infer()
