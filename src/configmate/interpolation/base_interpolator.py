import abc


class BaseInterpolator(abc.ABC):
    @abc.abstractmethod
    def interpolate_content(self, string: str) -> str:
        ...
