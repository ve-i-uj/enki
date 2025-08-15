import abc
import asyncio
from typing import Any

from enki.command import ICommand
from enki.core.message import Message
from enki.misc.result import Result
from enki.net.client import MsgTCPClient
from enki.net.inet import IClientMsgReceiver


class IApp(IClientMsgReceiver):
    """Application interface."""

    @property
    @abc.abstractmethod
    def is_connected(self) -> bool:
        """The application has been connected to the server."""

    @property
    @abc.abstractmethod
    def client(self) -> MsgTCPClient:
        """The client connected to the server."""

    @abc.abstractmethod
    def send_message(self, msg: Message) -> None:
        """Send the message to the server."""

    @abc.abstractmethod
    def send_command(self, cmd: ICommand) -> Any:
        pass

    @abc.abstractmethod
    async def stop(self):
        """Stop the application."""

    @abc.abstractmethod
    async def start(self, account_name: str, password: str) -> Result:
        """Start the application."""

    @abc.abstractmethod
    async def connect_to_loginapp(self) -> Result:
        pass

    @abc.abstractmethod
    def get_relogin_data(self) -> tuple[int, int]:
        pass

    @abc.abstractmethod
    def set_relogin_data(self, rnd_uuid: int, entity_id: int):
        """Set data that is necessary for relogin of application."""

    @abc.abstractmethod
    def wait_until_stop(self) -> asyncio.Future:
        pass

    @abc.abstractmethod
    async def create_account(self, account_name: str, password: str) -> Result:
        """Создать аккаунт."""

    @abc.abstractmethod
    async def reset_password(self, account_name: str) -> Result:
        """Скинуть пароль."""

    @abc.abstractmethod
    async def bind_account_email(
        self, entity_id: int, password: str, email: str
    ) -> Result:
        """Связать email с аккаунтом."""

    @abc.abstractmethod
    async def set_new_password(
        self, entity_id: int, oldpassword: str, newpassword: str
    ) -> Result:
        """Установить новый пароль."""

    @abc.abstractmethod
    def add_pending_msg(self, entity_id: int, msg: Message):
        pass

    @abc.abstractmethod
    def resend_pending_msgs(self, entity_id: int):
        pass
