import collections
import contextlib
import threading
from typing import Optional


class Context(collections.UserDict):
    ...


class ContextAccessMixin:
    def __init__(self) -> None:
        super().__init__()
        self._lock = threading.Lock()
        self._current_context: Optional[Context] = None

    @property
    def context(self) -> Context:
        if self._current_context is not None:
            return self._current_context
        raise RuntimeError("No context to infer parser with. see: `.attach_context()`")

    @context.setter
    def context(self, _) -> None:
        raise RuntimeError("Cannot set context directly. see: `.attach_context()`")

    @contextlib.contextmanager
    def attach_context(self, context: Context):
        """Attach a context to the parser to be used for inference"""
        with self._lock:
            self._current_context = context
            yield
            self._current_context = None
