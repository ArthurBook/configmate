"""
TODO: docs
"""

from configmate.core.functions import configure, get_config

__all__ = ["configure", "get_config"]

###
# Loads all plugins from the configmate_plugins package
# These are optional dependencies that extend configmate.
# You can find them in the plugins/ directory.
###
try:
    import configmate_plugins  # type: ignore
except ImportError:
    pass  # no plugins
else:
    import importlib
    import pkgutil

    ## Load all plugins
    for plugin in pkgutil.iter_modules(configmate_plugins.__path__):  # type: ignore
        importlib.import_module(f"{configmate_plugins.__name__}.{plugin.name}")  # type: ignore
