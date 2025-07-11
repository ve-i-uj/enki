"""Интерфейс для запускаемых объектов."""

import abc

from enki.misc.result import Result


class IStartable(abc.ABC):
    """Интерфейс запускаемого объекта."""

    @property
    @abc.abstractmethod
    def is_alive(self) -> bool:
        """Флаг запущен ли экземпляр класса."""

    @abc.abstractmethod
    async def start(self) -> Result:
        """Запустить объект."""

    @abc.abstractmethod
    def stop(self) -> None:
        """Остановить объект."""
