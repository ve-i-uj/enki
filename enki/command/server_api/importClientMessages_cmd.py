"""Команда для сбора протокола обмена сообщениями клиентского приложения.

Сбор описания сообщений с Loginapp и Baseapp.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from enki import msgspec
from enki.command.icommand import CommandResult, ICommand
from enki.command.loginapp import LoginappLoginCommand
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


@dataclass
class OnImportClientMessagesData:
    """Спецификация сообщения для компонентов клиент-серверного взаимодействия."""

    client_msg_specs: list[MsgDescr]
    loginapp_msg_specs: list[MsgDescr]
    baseapp_msg_specs: list[MsgDescr]


class OnImportClientMessagesCommandResult(CommandResult):
    """Результат выполнения команды по сбору описаний сообщений."""

    success: bool
    result: OnImportClientMessagesData | None = None
    text: str = ""


class ImportClientMessagesCommand(ICommand):
    """Команда для сбора описаний KBEngine-сообщений LoginApp, BaseApp, Client."""

    def __init__(
        self,
        account_name: str,
        password: str,
        loginapp_addr: Addr,
    ) -> None:
        """Конструктор.

        Args:
            account_name (str): имя аккаунта / логин
            password (str): пароль
            loginapp_addr (Addr): адрес Loginapp

        """
        self._account_name = account_name
        self._password = password
        self._loginapp_addr = loginapp_addr

    async def execute(self) -> OnImportClientMessagesCommandResult:
        """Выполнить команду.

        Returns:
            RequestMsgDescrsCommandResult: объект результата выполнения команды

        """
        # Request loginapp messages
        client = TcpMsgClient(self._loginapp_addr, ComponentType.CLIENT)
        start_res = await client.start()
        if not start_res.success:
            err_text = (
                f'Cannot connect to the "{self._loginapp_addr}" server address '
                f'(err="{start_res.text}")'
            )
            logger.error(err_text)
            return OnImportClientMessagesCommandResult(
                success=False, text=err_text
            )

        importClientMessages_msg = Message.create(  # noqa: N806
            msgspec.loginapp.importClientMessages, ()
        )
        success = await client.send_msg(importClientMessages_msg)
        if not success:
            err_text = (
                f'The message is not sent (msg = "{importClientMessages_msg}")'
            )
            logger.error("%s", err_text)
            return OnImportClientMessagesCommandResult(
                success=False, text=err_text
            )

        resp_msg = await client.wait_only_first_resp_msg(5 * SECOND)
        if resp_msg is None:
            err_text = "There is no response. Exit by timeout"
            logger.error("%s", err_text)
            return OnImportClientMessagesCommandResult(
                success=False, text=err_text
            )

        loginapp_res = OnImportClientMessagesMsgParser().parse(resp_msg)
        assert loginapp_res.result is not None

        login_cmd = LoginappLoginCommand(
            client_type=ClientType.BOTS,
            client_data=b"",
            login_name=self._account_name,
            password=self._password,
            digest="",  # При allowEmptyDigest=true он не нужен
            force_login=True,
            started_client=client,
        )
        login_res = await login_cmd.execute()
        if not login_res.success:
            return OnImportClientMessagesCommandResult(
                success=False, text=login_res.text
            )
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
            return OnImportClientMessagesCommandResult(
                success=False, text=start_res.text
            )

        importClientMessages_msg = Message.create(  # noqa: N806
            msgspec.baseapp.importClientMessages, ()
        )
        success = await client.send_msg(importClientMessages_msg)
        if not success:
            err_text = (
                f'The message is not sent (msg = "{importClientMessages_msg}")'
            )
            logger.error("%s", err_text)
            return OnImportClientMessagesCommandResult(
                success=False, text=err_text
            )

        resp_msg = await client.wait_only_first_resp_msg(5 * SECOND)
        client.stop()
        if resp_msg is None:
            err_text = "There is no response. Exit by timeout"
            logger.error("%s", err_text)
            return OnImportClientMessagesCommandResult(
                success=False, text=err_text
            )

        baseapp_res = OnImportClientMessagesMsgParser().parse(resp_msg)
        assert loginapp_res.result is not None

        specs = []
        specs.extend(loginapp_res.result.msg_specs)
        specs.extend(baseapp_res.result.msg_specs)

        app_msg_specs: dict[str, list[MsgDescr]] = {
            "client": [],
            "loginapp": [],
            "baseapp": [],
        }
        for msg_spec in specs:
            if msg_spec.name.startswith("Client"):
                app_msg_specs["client"].append(msg_spec)
            elif msg_spec.name.startswith("Loginapp"):
                app_msg_specs["loginapp"].append(msg_spec)
            elif msg_spec.name.startswith("Baseapp") or msg_spec.name.startswith(
                "Entity"
            ):
                app_msg_specs["baseapp"].append(msg_spec)
            else:
                err_text = f'Unknown type of the message "{msg_spec}"'
                return OnImportClientMessagesCommandResult(
                    success=False, text=err_text
                )

        return OnImportClientMessagesCommandResult(
            success=True,
            result=OnImportClientMessagesData(
                client_msg_specs=app_msg_specs["client"],
                loginapp_msg_specs=app_msg_specs["loginapp"],
                baseapp_msg_specs=app_msg_specs["baseapp"],
            ),
        )
