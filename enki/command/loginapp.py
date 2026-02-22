"""Commands for sending messages to LoginApp."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from enki import msgspec
from enki.kbeenum import ClientType, ComponentType, ServerError
from enki.kbetype.pytypes.basic_data_types import KBEBlob, KBEInt8, KBEString
from enki.msg.message import Message
from enki.msg_parser.client_msg_parser import (
    OnHelloCBMsgParser,
    OnLoginFailedMsgParser,
    OnLoginSuccessfullyMsgParser,
    OnScriptVersionNotMatchMsgParser,
    OnVersionNotMatchMsgParser,
)
from enki.settings import SECOND

from .icommand import CommandResult, ICommand

if TYPE_CHECKING:
    from enki.msg.msg_client import TcpMsgClient

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HelloCommandResultData:
    """Data result for Hello command.

    Attributes:
        kbe_version: KBEngine version.
        assets_version: Assets version.
        protocol_md5: Protocol MD5 hash.
        entity_def_md5: Entity definition MD5 hash.
        component_type: Component type.

    """

    kbe_version: str
    assets_version: str
    protocol_md5: str
    entity_def_md5: str
    component_type: ComponentType


@dataclass(frozen=True)
class HelloCommandResult(CommandResult):
    """Result of command 'hello'.

    Attributes:
        success: Whether the command was successful.
        result: Command result data.
        text: Additional text information.

    """

    success: bool
    result: HelloCommandResultData | None = None
    text: str = ""


class LoginappHelloCommand(ICommand):
    """LoginApp command 'hello'."""

    def __init__(
        self,
        kbe_version: str,
        script_version: str,
        encrypted_key: bytes,
        started_client: TcpMsgClient,
    ) -> None:
        """Initialize Hello command.

        Args:
            kbe_version: KBEngine version.
            script_version: Script version.
            encrypted_key: Encrypted key.
            started_client: Started TCP message client.

        """
        self._msg = Message.create(
            msgspec.loginapp.hello,
            values=(
                KBEString(kbe_version),
                KBEString(script_version),
                KBEBlob(encrypted_key),
            ),
        )
        assert started_client.is_started
        self._client = started_client

    async def execute(self) -> HelloCommandResult:
        """Execute the hello command.

        Returns:
            HelloCommandResult: The result of the command execution.

        """
        if not self._client.is_started:
            err_text = (
                f"[{self}] The client is not alive (client = '{self._client}', "
                f"msg = '{self._msg}')"
            )
            logger.warning(err_text)
            return HelloCommandResult(success=False, result=None, text=err_text)

        success = await self._client.send_msg(self._msg)
        if not success:
            err_text = (
                f"[{self}] The message is not sent (client = '{self._client}', "
                f"msg = '{self._msg}')"
            )
            logger.warning(err_text)
            return HelloCommandResult(success=False, text=err_text)

        resp_msg = await self._client.wait_only_first_resp_msg(5 * SECOND)
        if resp_msg is None:
            err_text = (
                f"[{self}] There is no response. Waiting stopped by timeout "
                f"(client = '{self._client}', msg = '{self._msg}')"
            )
            logger.warning(err_text)
            return HelloCommandResult(success=False, text=err_text)

        if resp_msg.id == msgspec.client.onVersionNotMatch.id:
            onVersionNotMatch_res = OnVersionNotMatchMsgParser().parse(resp_msg)  # noqa: N806
            assert onVersionNotMatch_res.result is not None
            onVersionNotMatch_pd = onVersionNotMatch_res.result  # noqa: N806

            plugin_kbe_version = self._msg.get_values()[0]
            server_kbe_version = onVersionNotMatch_pd.kbe_version
            msg = (
                f'Plugin designed for KBEngine version "{plugin_kbe_version}". '
                f'But actual KBEngine version is "{server_kbe_version}"'
            )
            return HelloCommandResult(success=False, text=msg)

        if resp_msg.id == msgspec.client.onScriptVersionNotMatch.id:
            onScriptVersionNotMatch_res = (  # noqa: N806
                OnScriptVersionNotMatchMsgParser().parse(resp_msg)
            )
            assert onScriptVersionNotMatch_res.result is not None
            onScriptVersionNotMatch_pd = onScriptVersionNotMatch_res.result  # noqa: N806

            plugin_assets_version = self._msg.get_values()[1]
            server_assets_version = onScriptVersionNotMatch_pd.assets_version
            msg = (
                f'Plugin designed for assets version "{plugin_assets_version}". '
                f'But actual script version is "{server_assets_version}"'
            )
            return HelloCommandResult(success=False, text=msg)

        onHelloCB_res = OnHelloCBMsgParser().parse(resp_msg)  # noqa: N806
        assert onHelloCB_res.result is not None

        onHelloCB_pd = onHelloCB_res.result  # noqa: N806

        return HelloCommandResult(
            success=True,
            result=HelloCommandResultData(
                onHelloCB_pd.kbe_version,
                onHelloCB_pd.assets_version,
                onHelloCB_pd.protocol_md5,
                onHelloCB_pd.entity_def_md5,
                onHelloCB_pd.component_type,
            ),
        )


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


class LoginappLoginCommand(ICommand):
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
        self._msg = Message.create(
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
        self._client = started_client

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
            return LoginappLoginCommandResult(
                success=False, result=None, text=err_text
            )

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


# @dataclass(frozen=True)
# class ReqAccountResetPasswordCommandResultData:
#     """Data result for request account reset password command.
#
#     Attributes:
#         code: Server error code.
#
#     """
#
#     code: ServerError = ServerError.MAX
#
#
# @dataclass(frozen=True)
# class ReqAccountResetPasswordCommandResult(CommandResult):
#     """Result of command 'reqAccountResetPassword'.
#
#     Attributes:
#         success: Whether the command was successful.
#         result: Command result data.
#         text: Additional text information.
#
#     """
#
#     success: bool
#     result: ReqAccountResetPasswordCommandResultData = field(
#         default_factory=lambda: ReqAccountResetPasswordCommandResultData()
#     )
#     text: str = ""
#
#
# class ReqAccountResetPasswordCommand(TCPCommand):
#     """LoginApp command 'reqAccountResetPassword'."""
#
#     def __init__(self, client: MsgTCPClient, account_name: str) -> None:
#         """Initialize request account reset password command.
#
#         Args:
#             client: TCP message client.
#             account_name: Account name.
#
#         """
#         super().__init__(client)
#         self._account_name = account_name
#
#         self._req_msg_spec = msgspec.loginapp.reqAccountResetPassword
#         self._success_resp_msg_spec = msgspec.client.onReqAccountResetPasswordCB
#         self._error_resp_msg_specs = []
#
#     async def execute(self) -> ReqAccountResetPasswordCommandResult:
#         """Execute the request account reset password command.
#
#         Returns:
#             ReqAccountResetPasswordCommandResult: The result of the command execution.
#
#         """
#         msg = Message(self._req_msg_spec, (self._account_name,))
#         await self._client.send_msg(msg)
#         resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
#         if resp_msg is None:
#             return ReqAccountResetPasswordCommandResult(
#                 False, text=self.get_timeout_err_text()
#             )
#
#         ret_code: int = resp_msg.get_values()[0]
#         code = ServerError(ret_code)
#         if code != ServerError.SUCCESS:
#             return ReqAccountResetPasswordCommandResult(False, text=code.name)
#
#         return ReqAccountResetPasswordCommandResult(
#             True, ReqAccountResetPasswordCommandResultData(code)
#         )
#
#
# class OnClientActiveTickCommand(TCPCommand):
#     """LoginAPp command 'onClientActiveTick'."""
#
#     def __init__(self, client: MsgTCPClient, timeout: float = 0.0) -> None:
#         """Initialize on client active tick command.
#
#         Args:
#             client: TCP message client.
#             timeout: Timeout value.
#
#         """
#         super().__init__(client)
#
#         self._req_msg_spec: MsgDescr = msgspec.loginapp.onClientActiveTick
#         self._success_resp_msg_spec: MsgDescr = msgspec.client.onAppActiveTickCB
#         self._error_resp_msg_specs: list[MsgDescr] = []
#
#         self._timeout = timeout

#     async def execute(self) -> CommandResult:
#         msg = Message(spec=self._req_msg_spec, fields=())
#         await self._client.send_msg(msg)
#         resp_msg = await self._waiting_for(self._timeout)
#         if resp_msg is None:
#             return CommandResult(
#                 False, f'No response for the "{self._req_msg_spec.name}"'
#             )

#         return CommandResult(True)


# @dataclass(frozen=True)
# class ReqCreateAccountCommandResultData:
#     code: ServerError = ServerError.MAX


# @dataclass(frozen=True)
# class ReqCreateAccountCommandResult(CommandResult):
#     success: bool
#     result: ReqCreateAccountCommandResultData
#     text: str


# class ReqCreateAccountCommand(TCPCommand):
#     """LoginAPp command 'reqCreateAccount'."""

#     def __init__(
#         self, client: MsgTCPClient, account_name: str, password: str, data: bytes
#     ) -> None:
#         super().__init__(client)
#         self._account_name = account_name
#         self._password = password
#         self._data = data

#         self._req_msg_spec = msgspec.loginapp.reqCreateAccount
#         self._success_resp_msg_spec = msgspec.client.onCreateAccountResult
#         self._error_resp_msg_specs = []

#     async def execute(self) -> ReqCreateAccountCommandResult:
#         msg = Message(
#             spec=self._req_msg_spec,
#             fields=(self._account_name, self._password, self._data),
#         )
#         await self._client.send_msg(msg)
#         resp_msg = await self._waiting_for()
#         if resp_msg is None:
#             return ReqCreateAccountCommandResult(
#                 False, text=self.get_timeout_err_text()
#             )

#         data: memoryview = resp_msg.get_values()[0]
#         ret_code, offset = UINT16.decode(data)
#         data = data[offset:]
#         code = ServerError(ret_code)
#         if code != ServerError.SUCCESS:
#             return ReqCreateAccountCommandResult(
#                 False, ReqCreateAccountCommandResultData(code), str(code)
#             )

#         return ReqCreateAccountCommandResult(
#             True, ReqCreateAccountCommandResultData(code)
#         )


# class ReqCreateMailAccountCommand(ReqCreateAccountCommand):
#     """LoginAPp command 'reqCreateMailAccount'."""

#     def __init__(
#         self, client: MsgTCPClient, account_name: str, password: str, data: bytes
#     ) -> None:
#         super().__init__(client, account_name, password, data)

#         self._req_msg_spec = msgspec.loginapp.reqCreateMailAccount


# @dataclass(frozen=True)
# class ImportClientSDKCommandResultData:
#     pending_files_number: int
#     file_name: str
#     data_size: int
#     data: memoryview


# @dataclass(frozen=True)
# class ImportClientSDKCommandResult(CommandResult):
#     success: bool
#     result: ImportClientSDKCommandResultData
#     text: str


# class ImportClientSDKCommand(TCPCommand):
#     _TIMEOUT = 5 * settings.SECOND

#     def __init__(
#         self,
#         client: MsgTCPClient,
#         options: str,
#         chunk_size: int,
#         cb_host: str,
#         cb_port: int,
#     ) -> None:
#         super().__init__(client)
#         self._options = options
#         self._chunk_size = chunk_size
#         self._cb_host = cb_host
#         self._cb_port = cb_port

#         self._req_msg_spec: MsgDescr = msgspec.loginapp.importClientSDK
#         self._success_resp_msg_spec: MsgDescr = msgspec.client.onImportClientSDK
#         self._error_resp_msg_specs: list[MsgDescr] = []

#     async def execute(self) -> ImportClientSDKCommandResult:
#         msg = Message(
#             spec=self._req_msg_spec,
#             fields=(
#                 self._options,
#                 self._chunk_size,
#                 self._cb_host,
#                 self._cb_port,
#             ),
#         )
#         await self._client.send_msg(msg)
#         resp_msg = await self._waiting_for(self._TIMEOUT)
#         if resp_msg is None:
#             return ImportClientSDKCommandResult(
#                 False, text=self.get_timeout_err_text()
#             )

#         data: memoryview = resp_msg.get_values()[0]
#         pending_files, offset = INT32.decode(data)
#         data = data[offset:]
#         file_name, offset = STRING.decode(data)
#         data = data[offset:]
#         data_size, offset = INT32.decode(data)
#         data = data[offset:]

#         return ImportClientSDKCommandResult(
#             True,
#             ImportClientSDKCommandResultData(
#                 pending_files, file_name, data_size, data
#             ),
#         )
