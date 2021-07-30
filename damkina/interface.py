"""Application interfaces."""

import abc

from enki import kbeclient, command


class IApp:
    """Application interface."""

    @abc.abstractmethod
    def send_message(self, msg: kbeclient.IMessage):
        """Send the message to the server."""
        pass

    @abc.abstractmethod
    def send_command(self, cmd: command.Command):
        pass
