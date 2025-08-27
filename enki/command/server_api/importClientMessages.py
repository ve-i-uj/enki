"""Команда для сбора протокола обмена сообщениями клиентского приложения.

Сбор описания сообщений с Loginapp и Baseapp.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from enki import msgspec
from enki.command.icommand import CommandResult, ICommand
from enki.command.loginapp import HelloCommand, LoginappLoginCommand
from enki.kbeenum import ClientType, ComponentType
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.msg_parser.client_msg_parser.client_msg_pasrser import (
    OnImportClientMessagesMsgParser,
)
from enki.net.addr import Addr, Port
from enki.settings import SECOND

if TYPE_CHECKING:
    from enki.msg.msg_descr import MsgDescr

logger = logging.getLogger(__name__)


class StopClientException(Exception):
    """Signal to stop the client."""


@dataclass
class OnImportClientMessagesData:
    msg_specs: list[MsgDescr]


class RequestMsgDescrsCommandResult(CommandResult):
    """Результат выполнения команды по сбору описаний сообщений."""

    success: bool
    result: OnImportClientMessagesData | None = None
    text: str = ""


class RequestMsgDescrsCommand(ICommand):
    def __init__(
        self,
        account_name: str,
        password: str,
        loginapp_addr: Addr,
        kbe_version: str,
        script_version: str,
        encrypted_key: bytes,
    ) -> None:
        self._account_name = account_name
        self._password = password
        self._loginapp_addr = loginapp_addr
        self._kbe_version = kbe_version
        self._script_version = script_version
        self._encrypted_key = encrypted_key

    async def execute(self) -> RequestMsgDescrsCommandResult:
        """Request LoginApp, BaseApp, ClientApp messages."""
        # Request loginapp messages
        client = TcpMsgClient(self._loginapp_addr, ComponentType.CLIENT)
        start_res = await client.start()
        if not start_res.success:
            err_text = (
                f'Cannot connect to the "{self._loginapp_addr}" server address '
                f'(err="{start_res.text}")'
            )
            logger.error(err_text)
            raise StopClientException

        importClientMessages_msg = Message.create(  # noqa: N806
            msgspec.loginapp.importClientMessages, ()
        )
        success = await client.send_msg(importClientMessages_msg)
        if not success:
            err_text = (
                f'The message is not sent (msg = "{importClientMessages_msg}")'
            )
            logger.error("%s", err_text)
            raise StopClientException(err_text)

        resp_msg = await client.wait_only_first_resp_msg(5 * SECOND)
        if resp_msg is None:
            err_text = "There is no response. Exit by timeout"
            logger.error("%s", err_text)
            raise StopClientException(err_text)

        loginapp_res = OnImportClientMessagesMsgParser().parse(resp_msg)
        assert loginapp_res.result is not None

        hello_cmd = HelloCommand(
            self._kbe_version, self._script_version, self._encrypted_key, client
        )

        res = await hello_cmd.execute()

        login_cmd = LoginappLoginCommand(
            client_type=ClientType.BOTS,
            client_data=b"",
            account_name=self._account_name,
            password=self._password,
            digest="",  # При allowEmptyDigest=true он не нужен
            force_login=True,
            started_client=client,
        )
        login_res = await login_cmd.execute()
        if not login_res.success:
            raise StopClientException(login_res.text)
        assert login_res.result is not None

        client.stop()

        baseapp_addr = Addr(
            ip_addr=login_res.result.host, port=Port(login_res.result.tcp_port)
        )
        client = TcpMsgClient(baseapp_addr, ComponentType.CLIENT)
        start_res = await client.start()
        if not start_res.success:
            err_text = (
                f'Cannot connect to the "{baseapp_addr}" server address '
                f'(err="{start_res.text}")'
            )
            logger.error(err_text)
            raise StopClientException

        importClientMessages_msg = Message.create(
            msgspec.baseapp.importClientMessages, ()
        )
        success = await client.send_msg(importClientMessages_msg)
        if not success:
            err_text = (
                f'The message is not sent (msg = "{importClientMessages_msg}")'
            )
            logger.error("%s", err_text)
            raise StopClientException(err_text)

        resp_msg = await client.wait_only_first_resp_msg(5 * SECOND)
        client.stop()
        if resp_msg is None:
            err_text = "There is no response. Exit by timeout"
            logger.error("%s", err_text)
            raise StopClientException(err_text)

        baseapp_res = OnImportClientMessagesMsgParser().parse(resp_msg)
        assert loginapp_res.result is not None

        res = []
        res.extend(loginapp_res.result.msg_specs)
        res.extend(baseapp_res.result.msg_specs)
        return res
