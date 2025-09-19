"""Команда для запроса описания сущностей с Baseapp.

В опсании будут сущности, методы, свойства. Для получения нужен логин
на Loginapp, чтобы получить адрес Baseapp.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from enki import msgspec
from enki.command.icommand import CommandResult, ICommand
from enki.command.loginapp import LoginappLoginCommand
from enki.kbeenum import ClientType, ComponentType
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.msg_parser.client_msg_parser.importClientEntityDef_msg_parser import (
    OnImportClientEntityDefMsgParser,
    ParsedEntityInfo,
    ParsedTypeInfo,
)
from enki.net.addr import Addr, Port
from enki.settings import SECOND

logger = logging.getLogger(__name__)


@dataclass
class OnImportClientEntityDefData:
    """Спецификация сообщения для компонентов клиент-серверного взаимодействия."""

    types: list[ParsedTypeInfo]
    entities: list[ParsedEntityInfo]


class OnImportClientEntityDefCommandResult(CommandResult):
    """Результат выполнения команды по сбору описаний сообщений."""

    success: bool
    result: OnImportClientEntityDefData | None = None
    text: str = ""


class ImportClientEntityDefCommand(ICommand):
    """Команда для получения от Baseapp описание сущностей.

    Описание включает типы данных, типы сущностей их методы удалённого вызова
    и свойства.
    """

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

    async def execute(self) -> OnImportClientEntityDefCommandResult:
        """Выполнить команду.

        Returns:
            OnImportClientEntityDefCommandResult: объект результата выполнения
                команды

        """
        loginapp_client = TcpMsgClient(self._loginapp_addr, ComponentType.CLIENT)
        start_res = await loginapp_client.start()
        if not start_res.success:
            err_text = (
                f'Cannot connect to the "{self._loginapp_addr}" server address '
                f'(err="{start_res.text}")'
            )
            logger.error(err_text)
            return OnImportClientEntityDefCommandResult(
                success=False, text=err_text
            )

        login_cmd = LoginappLoginCommand(
            client_type=ClientType.BOTS,
            client_data=b"",
            login_name=self._account_name,
            password=self._password,
            digest="",  # При allowEmptyDigest=true он не нужен
            force_login=True,
            started_client=loginapp_client,
        )
        login_res = await login_cmd.execute()
        if not login_res.success:
            return OnImportClientEntityDefCommandResult(
                success=False, text=login_res.text
            )
        assert login_res.result is not None

        loginapp_client.stop()

        baseapp_addr = Addr(
            ip_addr=login_res.result.host, port=Port(login_res.result.tcp_port)
        )
        baseapp_client = TcpMsgClient(baseapp_addr, ComponentType.CLIENT)
        start_res = await baseapp_client.start()
        if not start_res.success:
            err_text = (
                f'Cannot connect to the "{baseapp_addr}" server address '
                f'(err="{start_res.text}")'
            )
            logger.error(err_text)
            return OnImportClientEntityDefCommandResult(
                success=False, text=start_res.text
            )

        importClientEntityDef_msg = Message.create(  # noqa: N806
            msgspec.baseapp.importClientEntityDef, ()
        )
        success = await baseapp_client.send_msg(importClientEntityDef_msg)
        if not success:
            err_text = (
                f'The message is not sent (msg = "{importClientEntityDef_msg}")'
            )
            logger.error("%s", err_text)
            return OnImportClientEntityDefCommandResult(
                success=False, text=err_text
            )

        resp_msg = await baseapp_client.wait_only_first_resp_msg(5 * SECOND)
        baseapp_client.stop()
        if resp_msg is None:
            err_text = "There is no response. Exit by timeout"
            logger.error("%s", err_text)
            return OnImportClientEntityDefCommandResult(
                success=False, text=err_text
            )

        onImportClientEntityDef_res = OnImportClientEntityDefMsgParser().parse(  # noqa: N806
            resp_msg
        )
        assert onImportClientEntityDef_res.result is not None

        ent_res = onImportClientEntityDef_res.result
        return OnImportClientEntityDefCommandResult(
            success=True,
            result=OnImportClientEntityDefData(
                types=ent_res.types, entities=ent_res.entities
            ),
        )
