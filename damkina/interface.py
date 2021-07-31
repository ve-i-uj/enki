"""Application interfaces."""

import abc
from typing import Any

from enki import kbeclient, command


class IApp:
    """Application interface."""

    @property
    @abc.abstractmethod
    def client(self) -> kbeclient.IClient:
        """The client connected to the server."""
        pass

    @abc.abstractmethod
    def send_message(self, msg: kbeclient.IMessage) -> None:
        """Send the message to the server."""
        pass

    @abc.abstractmethod
    def send_command(self, cmd: command.Command) -> Any:
        pass
