"""Application interfaces."""

import abc
from typing import Any

from enki import command
from enki.interface import IClient, IMessage, IMsgReceiver


class IApp(IMsgReceiver):
    """Application interface."""

    @property
    @abc.abstractmethod
    def client(self) -> IClient:
        """The client connected to the server."""
        pass

    @abc.abstractmethod
    def send_message(self, msg: IMessage) -> None:
        """Send the message to the server."""
        pass

    @abc.abstractmethod
    def send_command(self, cmd: command.Command) -> Any:
        pass
