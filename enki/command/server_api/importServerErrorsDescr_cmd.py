"""Команда для сбора протокола обмена сообщениями клиентского приложения.

Сбор описания сообщений с Loginapp и Baseapp.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from enki import msgspec
from enki.command.icommand import CommandResult, ICommand
from enki.kbeenum import ComponentType
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.msg_parser.client_msg_parser.onImportServerErrorsDescr_msg_parser import (  # noqa: E501
    OnImportServerErrorsDescrMsgParser,
    ParsedServerErrorInfo,
)
from enki.settings import SECOND

if TYPE_CHECKING:
    from enki.net.addr import Addr

logger = logging.getLogger(__name__)


@dataclass
class ImportServerErrorsDescrCommandResultData:
    """Data result for import server errors description command.

    Attributes:
        descrs: List of parsed server error information.

    """

    descrs: list[ParsedServerErrorInfo]


@dataclass(frozen=True)
class ImportServerErrorsDescrCommandResult(CommandResult):
    """Result of command 'importServerErrorsDescr'.

    Attributes:
        success: Whether the command was successful.
        result: Command result data.
        text: Additional text information.

    """

    success: bool
    result: ImportServerErrorsDescrCommandResultData | None = None
    text: str = ""


class ImportServerErrorsDescrCommand(ICommand):
    """LoginApp command 'importServerErrorsDescr'."""

    def __init__(self, loginapp_addr: Addr) -> None:
        """Initialize import server errors description command.

        Args:
            loginapp_addr: LoginApp address.

        """
        self._loginapp_addr = loginapp_addr

    async def execute(self) -> ImportServerErrorsDescrCommandResult:
        """Execute the import server errors description command.

        Returns:
            ImportServerErrorsDescrCommandResult: The result of the command
                execution.

        """
        client = TcpMsgClient(self._loginapp_addr, ComponentType.CLIENT)
        start_res = await client.start()
        if not start_res.success:
            err_text = (
                f'Cannot connect to the "{self._loginapp_addr}" server address '
                f'(err="{start_res.text}")'
            )
            logger.error(err_text)
            return ImportServerErrorsDescrCommandResult(
                success=False, text=err_text
            )

        msg = Message.create(msgspec.loginapp.importServerErrorsDescr, ())

        logger.info("[%s] Send the message ...", self)
        success = await client.send_msg(msg)
        if not success:
            client.stop()
            err_text = (
                f"[{self}] The message is not sent (client = '{client}', "
                "msg = '{self._msg}')"
            )
            logger.warning(err_text)
            return ImportServerErrorsDescrCommandResult(
                success=False, result=None, text=err_text
            )

        logger.info("[%s] The message was sent. Waiting for response ...", self)
        resp_msg = await client.wait_only_first_resp_msg(5 * SECOND)
        if resp_msg is None:
            client.stop()
            err_text = (
                f"[{self}] There is no response. Waiting stopped by timeout or "
                f"closed by the server"
            )
            logger.warning(err_text)
            return ImportServerErrorsDescrCommandResult(
                success=False, result=None, text=err_text
            )

        client.stop()

        res = OnImportServerErrorsDescrMsgParser().parse(resp_msg)
        assert res.success
        assert res.result is not None

        assert resp_msg.id == msgspec.client.onImportServerErrorsDescr.id

        return ImportServerErrorsDescrCommandResult(
            success=True,
            result=ImportServerErrorsDescrCommandResultData(
                descrs=res.result.server_error_infos
            ),
        )
