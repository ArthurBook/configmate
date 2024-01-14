"""
"""
import sys

if sys.version_info < (3, 10):
    import importlib_metadata  # type: ignore
else:
    import importlib.metadata as importlib_metadata  # type: ignore

discovered_plugins = importlib_metadata.entry_points(group="configmate_plugins")
for p in discovered_plugins:
    p.load()

from configmate.core.functions import configure, get_config
