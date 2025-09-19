"""Интерфейс для запускаемых объектов."""

import abc
from typing import TypeAlias

LoopPeriod: TypeAlias = float


# class PeriodicalTaskResult(Result):
#     """Результат выполнения периодической задачи."""

#     success: bool
#     result: Any = None
#     text: str = ""


class IPeriodicalTask(abc.ABC):
    """Задача, которая выполняется периодически."""

    @abc.abstractmethod
    async def start_periodical_task(self) -> None:
        """Запустить периодическую задачу."""

    @abc.abstractmethod
    def stop_periodical_task(self) -> None:
        """Остановить периодическую задачу."""

    # @abc.abstractmethod
    # def get_last_result(self) -> PeriodicalTaskResult:
    #     """Получить последний результат выполнения."""
