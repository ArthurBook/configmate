import json
import os
import re
import sys
import types

UTF8 = "utf-8"

CLI_FILE_OVERLAY_PREFIX = "+"
CLI_ARG_OVERLAY_KEY_PREFIX = "++"
CLI_ARG_OVERLAY_KEY_DELIMITER = "."
CLI_ARG_OVERLAY_ARG_PARSER = json.loads
CLI_SECTION_END_TOKEN = "/"

CLI_ARGS = sys.argv
ENVIRONMENT = types.MappingProxyType(os.environ)
BASH_VAR_PATTERN = re.compile(r"\${(?P<variable>\w+)(?::(?P<default_value>[^}:]+))?}")

OVERLAY = "overlay"
