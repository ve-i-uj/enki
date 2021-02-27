from __future__ import annotations
import abc
import asyncio
import logging
from typing import Union, List, Dict, Awaitable, Any, Tuple, ClassVar
from dataclasses import dataclass

from enki import settings
from enki import message, interface
from enki.misc import devonly

from . import kbeclientutils


logger = logging.getLogger(__name__)


class _Command(interface.IReturningCommand,
               interface.IMsgReceiver,
               interface.IMsgRespAwaitable,
               kbeclientutils.MsgRespAwaitableMixIn):
    """Abstract class for commands."""

    _req_msg_spec: ClassVar[message.MessageSpec]
    _success_resp_msg_spec: ClassVar[message.MessageSpec]
    _error_resp_msg_specs: ClassVar[List[message.MessageSpec]]

    def on_receive_msg(self, msg: interface.IMessage) -> bool:
        return kbeclientutils.MsgRespAwaitableMixIn.on_receive_msg(self, msg)

    async def send(self, msg: interface.IMessage) -> None:
        """Send the message."""
        return await kbeclientutils.MsgRespAwaitableMixIn.send(self, msg)

    def waiting_for(self, success_msg_spec: int, error_msg_specs: List[int], timeout: int
                    ) -> Awaitable[interface.IMessage]:
        return kbeclientutils.MsgRespAwaitableMixIn.waiting_for(
            self, success_msg_spec, error_msg_specs, timeout
        )

    @abc.abstractmethod
    def execute(self) -> Any:
        pass


class LoginAppHelloCommand(_Command):
    """LoginApp command 'hello'."""

    _req_msg_spec: message.MessageSpec = message.app.loginapp.hello
    _success_resp_msg_spec: message.MessageSpec = message.app.client.onHelloCB
    _error_resp_msg_specs: List[message.MessageSpec] = [
        message.app.client.onVersionNotMatch,
        message.app.client.onScriptVersionNotMatch,
    ]

    def __init__(self, kbe_version: str, script_version: str, encrypted_key: str,
                 client: interface.IClient):
        super().__init__(client)
        self._msg = message.Message(
            spec=self._req_msg_spec,
            fields=(kbe_version, script_version, encrypted_key)
        )

    async def execute(self) -> Tuple[bool, str]:
        await self.send(self._msg)
        resp_msg = await self.waiting_for(self._success_resp_msg_spec,
                                          self._error_resp_msg_specs,
                                          settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg.id == message.app.client.onVersionNotMatch.id:
            kbe_version = self._msg.get_values()[0]
            actual_kbe_version = resp_msg.get_values()[0]
            msg = f'Plugin designed for KBEngine version "{kbe_version}". ' \
                  f'But actual KBEngine version is "{actual_kbe_version}"'
            return False, msg

        if resp_msg.id == message.app.client.onScriptVersionNotMatch.id:
            script_version = self._msg.get_values()[1]
            actual_script_version = resp_msg.get_values()[0]
            msg = f'Plugin designed for script version "{script_version}". ' \
                  f'But actual script version is "{actual_script_version}"'
            return False, msg

        return True, ''


class LoginAppLoginCommand(_Command):
    _req_msg_spec: message.MessageSpec = message.app.loginapp.login
    _resp_msg_specs: List[message.MessageSpec] = [
        message.app.client.onLoginSuccessfully,
        message.app.client.onLoginFailed,
    ]

    def __init__(self, args: Tuple[Any, ...], client: interface.IClient):
        super().__init__(client)
        self._args = args

    async def execute(self) -> None:
        pass
