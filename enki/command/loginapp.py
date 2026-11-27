"""Commands for sending messages to LoginApp."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from enki import msgspec
from enki.kbeenum import ClientType, ServerError
from enki.kbetype.pytypes.basic_data_types import KBEBlob, KBEInt8, KBEString
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.msg_parser.client_msg_parser import (
    OnLoginFailedMsgParser,
    OnLoginSuccessfullyMsgParser,
)
from enki.settings import SECOND

from .icommand import CommandResult, ICommand

if TYPE_CHECKING:
    from enki.msg.msg_client import TcpMsgClient

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoginappLoginCommandResultData:
    """Data result for LoginApp login command.

    Attributes:
        ret_code: Return code.
        account_name: Account name.
        host: Host address.
        tcp_port: TCP port.
        udp_port: UDP port.
        data: Additional data.

    """

    ret_code: ServerError
    account_name: str = ""
    host: str = ""
    tcp_port: int = 0
    udp_port: int = 0
    data: bytes = b""


@dataclass(frozen=True)
class LoginappLoginCommandResult(CommandResult):
    """Result of command 'login'.

    Attributes:
        success: Whether the command was successful.
        result: Command result data.
        text: Additional text information.

    """

    success: bool
    result: LoginappLoginCommandResultData | None = None
    text: str = ""


class LoginappLoginCommand(ICommand[LoginappLoginCommandResult]):
    """LoginApp command 'login'."""

    def __init__(
        self,
        client_type: ClientType,
        client_data: bytes,
        login_name: str,
        password: str,
        digest: str,
        force_login: bool,
        started_client: TcpMsgClient,
    ) -> None:
        """Initialize LoginApp login command.

        Args:
            client_type: Client type.
            client_data: Client data.
            login_name: Account name.
            password: Password.
            digest: Digest.
            force_login: Whether to force login.
            started_client: Started TCP message client.

        """
        self._msg: Message = Message.create(
            msgspec.loginapp.login,
            values=(
                KBEInt8(client_type.value),
                KBEBlob(client_data),
                KBEString(login_name),
                KBEString(password),
                KBEString(digest),
                KBEString("1" if force_login else ""),
            ),
        )
        assert started_client.is_started
        self._client: TcpMsgClient = started_client

    @override
    async def execute(self) -> LoginappLoginCommandResult:
        """Execute the login command.

        Returns:
            LoginappLoginCommandResult: The result of the command execution.

        """
        if not self._client.is_started:
            err_text = (
                f"[{self}] The "
                f"client is not alive (client = '{self._client}', msg = '{self._msg}')"
            )
            logger.warning(err_text)
            return LoginappLoginCommandResult(success=False, result=None, text=err_text)

        logger.info("[%s] Send the message ...", self)
        success = await self._client.send_msg(self._msg)
        if not success:
            err_text = (
                f"[{self}] The message is not sent (client = '{self._client}', "
                f"msg = '{self._msg}')"
            )
            logger.warning(err_text)
            return LoginappLoginCommandResult(success=False, text=err_text)

        logger.info("[%s] The message was sent. Waiting for response ...", self)
        resp_msg = await self._client.wait_only_first_resp_msg(5 * SECOND)
        if resp_msg is None:
            err_text = (
                f"[{self}] There is no response. Waiting stopped by timeout or "
                f"closed by the server"
            )
            logger.warning(err_text)
            return LoginappLoginCommandResult(success=False, text=err_text)

        if resp_msg.id == msgspec.client.onLoginFailed.id:
            onLoginFailed_res = OnLoginFailedMsgParser().parse(resp_msg)  # noqa: N806
            assert onLoginFailed_res.result is not None
            onLoginFailed_pd = onLoginFailed_res.result  # noqa: N806

            err_text = (
                f"Login Falied (reason = "
                f"'{onLoginFailed_pd.ret_code.name}', data = "
                f"'{onLoginFailed_pd.data.decode()}')"
            )
            logger.info("%s", err_text)
            return LoginappLoginCommandResult(
                success=False,
                result=LoginappLoginCommandResultData(
                    ret_code=onLoginFailed_pd.ret_code, data=onLoginFailed_pd.data
                ),
                text=err_text,
            )

        res = OnLoginSuccessfullyMsgParser().parse(resp_msg)
        assert res.result is not None
        pd = res.result

        logger.debug("[%s] pd = %s", self, pd)
        return LoginappLoginCommandResult(
            success=True,
            result=LoginappLoginCommandResultData(
                ServerError.SUCCESS,
                pd.account_name,
                pd.host,
                pd.baseapp_tcp_address.port,
                pd.baseapp_udp_address.port,
                pd.data,
            ),
        )
