import abc
import asyncio
from typing import Any

from enki.enkitype import Result
from enki.net.kbeclient import IClient, IMessage, IMsgReceiver, Message
from enki.net.command import ICommand
from enki.net.msgspec import default_kbenginexml
from enki.net.netentity import IEntityRPCSerializer, EntityComponentRPCSerializer

from .layer import GameLayer


class IApp(IMsgReceiver):
    """Application interface."""

    @property
    @abc.abstractmethod
    def game(self) -> GameLayer:
        """The game layer."""
        pass

    @property
    @abc.abstractmethod
    def is_connected(self) -> bool:
        """The application has been connected to the server."""
        pass

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
    def send_command(self, cmd: ICommand) -> Any:
        pass

    @abc.abstractmethod
    def stop(self):
        """Stop the application."""
        pass

    @abc.abstractmethod
    def start(self, account_name: str, password: str) -> Result:
        """Start the application."""
        pass

    @abc.abstractmethod
    def get_relogin_data(self) -> tuple[int, int]:
        pass

    @abc.abstractmethod
    def set_relogin_data(self, rnd_uuid: int, entity_id: int):
        """Set data that is necessary for relogin of application."""
        pass

    @abc.abstractmethod
    def get_kbenginexml(self) -> default_kbenginexml.root:
        pass

    @abc.abstractmethod
    def wait_until_stop(self) -> asyncio.Future:
        pass


# TODO: [2022-11-12 08:39 burov_alexey@mail.ru]:
# Пока сюда. После удачной генерации можно вынести в eserializer.py

class IAppEntityRPCSerializer(IEntityRPCSerializer):

    def __init__(self, app: IApp) -> None:
        super().__init__()
        self._app = app

    def send_remote_call_msg(self, msg: Message):
        self._app.send_message(msg)


class IAppEntityComponentRPCSerializer(EntityComponentRPCSerializer):

    def __init__(self, e_serializer: IAppEntityRPCSerializer, own_attr_id: int) -> None:
        super().__init__(e_serializer, own_attr_id)

    def send_remote_call_msg(self, msg: Message):
        self._e_serializer.send_remote_call_msg(msg)
