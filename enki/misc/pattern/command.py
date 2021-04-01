"""Interfaces for the pattern 'Command'.

https://en.wikipedia.org/wiki/Command_pattern
"""

import abc


class IClient(abc.ABC):
    pass


class ICommand(abc.ABC):

    @abc.abstractmethod
    def execute(self) -> None:
        pass


class IInvoker(abc.ABC):

    @abc.abstractmethod
    def add_command(self, command: ICommand) -> None:
        pass


class IReceiver(abc.ABC):
    pass
