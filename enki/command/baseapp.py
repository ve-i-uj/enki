"""Commands for sending messages to BaseApp."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from enki import msgspec
from enki.kbetype.pytypes.basic_data_types import KBEBlob, KBEString
from enki.msg.message import Message
from enki.msg_parser.client_msg_parser.client_msg_pasrser import (
    OnHelloCBMsgParser,
    OnScriptVersionNotMatchMsgParser,
    OnVersionNotMatchMsgParser,
)
from enki.settings import SECOND

from .icommand import CommandResult, ICommand

if TYPE_CHECKING:
    from enki.kbeenum import ComponentType
    from enki.msg.msg_client import TcpMsgClient

logger = logging.getLogger(__name__)


@dataclass
class BaseappHelloCommandResultData:
    """Данные при удачном ответе на Baseapp::hello."""

    kbe_version: str
    assets_version: str
    protocol_md5: str
    entity_def_md5: str
    component_type: ComponentType


@dataclass(frozen=True)
class BaseappHelloCommandResult(CommandResult):
    """Результат выполнения команды Baseapp::hello."""

    success: bool
    result: BaseappHelloCommandResultData | None = None
    text: str = ""


class BaseappHelloCommand(ICommand):
    """BaseApp command 'hello'."""

    def __init__(
        self,
        kbe_version: str,
        script_version: str,
        encrypted_key: bytes,
        started_client: TcpMsgClient,
        resp_timeout: float,
    ) -> None:
        """Конструктор команды.

        Args:
            kbe_version (str): версия KBEngine
            script_version (str): версия скриптов (кода на питоне / assets'ов)
            encrypted_key (bytes): зашифрованный ключ
            started_client (bytes): запущенный клиент к Baseapp
            resp_timeout (float): время ожидания ответа от Baseapp

        """
        self._msg = Message.create(
            msgspec.baseapp.hello,
            (
                KBEString(kbe_version),
                KBEString(script_version),
                KBEBlob(encrypted_key),
            ),
        )

        assert started_client.is_alive
        self._client = started_client
        self._resp_timeout = resp_timeout

    async def execute(self) -> BaseappHelloCommandResult:
        """Execute the hello command.

        Returns:
            BaseappHelloCommandResult: The result of the command execution.

        """
        if not self._client.is_alive:
            text = (
                f"[{self}] The client is not alive (client = '{self._client}', "
                f"msg = '{self._msg}')"
            )
            logger.warning(text)
            return BaseappHelloCommandResult(
                success=False, result=None, text=text
            )

        success = await self._client.send_msg(self._msg)
        if not success:
            text = (
                f"[{self}] The message is not sent (client = '{self._client}', "
                f"msg = '{self._msg}')"
            )
            logger.warning(text)
            return BaseappHelloCommandResult(success=False, text=text)

        resp_msg = await self._client.wait_only_first_resp_msg(5 * SECOND)
        if resp_msg is None:
            text = (
                f"[{self}] There is no response. Waiting stopped by timeout "
                f"(client = '{self._client}', msg = '{self._msg}')"
            )
            logger.warning(text)
            return BaseappHelloCommandResult(success=False, text=text)

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
            return BaseappHelloCommandResult(success=False, text=msg)

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
            return BaseappHelloCommandResult(success=False, text=msg)

        onHelloCB_res = OnHelloCBMsgParser().parse(resp_msg)  # noqa: N806
        assert onHelloCB_res.result is not None

        onHelloCB_pd = onHelloCB_res.result  # noqa: N806

        return BaseappHelloCommandResult(
            success=True,
            result=BaseappHelloCommandResultData(
                onHelloCB_pd.kbe_version,
                onHelloCB_pd.assets_version,
                onHelloCB_pd.protocol_md5,
                onHelloCB_pd.entity_def_md5,
                onHelloCB_pd.component_type,
            ),
        )


# class OnClientActiveTickCommand(ICommand):
#     """BaseApp command 'onClientActiveTick'."""

#     def __init__(self, client: MsgTCPClient, timeout: float = 0.0) -> None:
#         self._req_msg_spec: MsgDescr = msgspec.baseapp.onClientActiveTick
#         self._success_resp_msg_spec: MsgDescr = msgspec.client.onAppActiveTickCB
#         self._error_resp_msg_specs: list[MsgDescr] = []

#         self._timeout = timeout
#         self._msg = Message(spec=self._req_msg_spec, fields=())

#     async def execute(self) -> CommandResult:
#         await self._client.send_msg(self._msg)
#         resp_msg = await self._waiting_for(self._timeout)
#         if resp_msg is None:
#             return CommandResult(
#                 False, f'No response for the "{self._req_msg_spec.name}"'
#             )

#         return CommandResult(True)


# class LoginBaseappCommand(icommand.TCPCommand):
#     def __init__(
#         self, client: MsgTCPClient, account_name: str, password: str
#     ) -> None:
#         super().__init__(client)
#         self._account_name = account_name
#         self._password = password

#         self._req_msg_spec = msgspec.baseapp.loginBaseapp
#         self._success_resp_msg_spec = None
#         self._error_resp_msg_specs = [msgspec.client.onLoginBaseappFailed]

#     async def execute(self) -> CommandResult:
#         msg = Message(
#             msgspec.baseapp.loginBaseapp,
#             (self._account_name, self._password),
#         )
#         await self._client.send_msg(msg)
#         resp_msg = await self._waiting_for()
#         if resp_msg is None:
#             # Good. There were no error messages.
#             return CommandResult(True, "")
#         err_code = resp_msg.get_values()[0]
#         err_name = ServerError(err_code).name
#         text = f"The client cannot connect to the BaseApp ({err_name})"
#         return CommandResult(False, text)


# @dataclass
# class ReloginBaseappCommandResultData:
#     rnd_uuid: int = NoValue.NO_ID


# @dataclass
# class ReloginBaseappCommandResult(CommandResult):
#     success: bool
#     result: ReloginBaseappCommandResultData
#     text: str = ""


# class ReloginBaseappCommand(icommand.TCPCommand):
#     def __init__(
#         self,
#         account_name: str,
#         password: str,
#         rnd_uuid: int,
#         entity_id: int,
#         client: MsgTCPClient,
#     ) -> None:
#         super().__init__(client)
#         self._account_name = account_name
#         self._password = password
#         self._rnd_uuid = rnd_uuid
#         self._entity_id = entity_id

#         self._req_msg_spec = msgspec.baseapp.reloginBaseapp
#         self._success_resp_msg_spec: MsgDescr = (
#             msgspec.client.onReloginBaseappSuccessfully
#         )
#         self._error_resp_msg_specs = [msgspec.client.onReloginBaseappFailed]

#     async def execute(self) -> ReloginBaseappCommandResult:
#         msg = Message(
#             self._req_msg_spec,
#             (
#                 self._account_name,
#                 self._password,
#                 self._rnd_uuid,
#                 self._entity_id,
#             ),
#         )
#         await self._client.send_msg(msg)
#         resp_msg = await self._waiting_for()
#         if resp_msg is None:
#             return ReloginBaseappCommandResult(
#                 False,
#                 ReloginBaseappCommandResultData(),
#                 self.get_timeout_err_text(),
#             )

#         if resp_msg.id in [s.id for s in self._error_resp_msg_specs]:
#             err_code: int = resp_msg.get_values()[0]
#             err_text = ServerError(err_code).name
#             return ReloginBaseappCommandResult(
#                 False,
#                 ReloginBaseappCommandResultData(),
#                 f"It cannot relogin to the BaseApp ({err_text})",
#             )

#         rnd_uuid: int = resp_msg.get_values()[0]
#         return ReloginBaseappCommandResult(
#             True, ReloginBaseappCommandResultData(rnd_uuid)
#         )


# @dataclass
# class ReqAccountNewPasswordCommandResultData:
#     code: ServerError


# @dataclass
# class ReqAccountNewPasswordResult(CommandResult):
#     success: bool
#     result: ReqAccountNewPasswordCommandResultData
#     text: str = ""


# class ReqAccountNewPasswordCommand(icommand.TCPCommand):
#     def __init__(
#         self, client: MsgTCPClient, entity_id: int, old_pwd: str, new_pwd: str
#     ) -> None:
#         super().__init__(client)
#         self._entity_id = entity_id
#         self._old_pwd = old_pwd
#         self._new_pwd = new_pwd

#         self._req_msg_spec = msgspec.baseapp.reqAccountNewPassword
#         self._success_resp_msg_spec: MsgDescr = (
#             msgspec.client.onReqAccountNewPasswordCB
#         )
#         self._error_resp_msg_specs = []

#     async def execute(self) -> ReqAccountNewPasswordResult:
#         msg = Message(
#             self._req_msg_spec, (self._entity_id, self._old_pwd, self._new_pwd)
#         )
#         await self._client.send_msg(msg)
#         resp_msg = await self._waiting_for()
#         if resp_msg is None:
#             return ReqAccountNewPasswordResult(
#                 False, text=self.get_timeout_err_text()
#             )

#         # It's the "onReqAccountNewPasswordCB" message because no answer if something's wrong.
#         ret_code: int = resp_msg.get_values()[0]
#         if ServerError(ret_code) != ServerError.SUCCESS:
#             return ReqAccountNewPasswordResult(
#                 False, text=ServerError(ret_code).name
#             )
#         return ReqAccountNewPasswordResult(
#             True, ReqAccountNewPasswordCommandResultData(ServerError(ret_code))
#         )


# class LogoutBaseappCommand(icommand.TCPCommand):
#     """The client connection will be closed by the server after this command executes."""

#     def __init__(
#         self, client: MsgTCPClient, rnd_uuid: int, entity_id: int
#     ) -> None:
#         super().__init__(client)
#         self._rnd_uuid = rnd_uuid
#         self._entity_id = entity_id

#         self._req_msg_spec = msgspec.baseapp.logoutBaseapp
#         self._success_resp_msg_spec = None
#         self._error_resp_msg_specs = []

#     async def execute(self):
#         msg = Message(self._req_msg_spec, (self._rnd_uuid, self._entity_id))
#         await self._client.send_msg(msg)
#         return CommandResult(True, None, "")


# class OnUpdateDataFromClientCommand(icommand.TCPCommand):
#     def __init__(
#         self,
#         client: MsgTCPClient,
#         position: Position,
#         direction: Direction,
#         is_on_ground: bool,
#         space_id: int,
#     ) -> None:
#         super().__init__(client)
#         self._position = position
#         self._direction = direction
#         self._is_on_ground = is_on_ground
#         self._space_id = space_id

#         self._req_msg_spec = msgspec.baseapp.onUpdateDataFromClient
#         self._success_resp_msg_spec = None
#         self._error_resp_msg_specs = []

#     async def execute(self):
#         msg = Message(
#             self._req_msg_spec,
#             (
#                 self._position.x,
#                 self._position.y,
#                 self._position.z,
#                 self._direction.x,
#                 self._direction.y,
#                 self._direction.z,
#                 self._is_on_ground,
#                 self._space_id,
#             ),
#         )
#         await self._client.send_msg(msg)
#         # The "onUpdateBasePos" message only will be sent to the client in
#         # the server messages. The response mush be handled in the application
#         # handler because there is no direct responses for this request.
#         return CommandResult(True, None, "")


# class OnUpdateDataFromClientForControlledEntityCommand(icommand.TCPCommand):
#     def __init__(
#         self,
#         client: MsgTCPClient,
#         entity_id: int,
#         position: Position,
#         direction: Direction,
#         is_on_ground: bool,
#         space_id: int,
#     ) -> None:
#         super().__init__(client)
#         self._entity_id = entity_id
#         self._position = position
#         self._direction = direction
#         self._is_on_ground = is_on_ground
#         self._space_id = space_id

#         self._req_msg_spec = (
#             msgspec.baseapp.onUpdateDataFromClientForControlledEntity
#         )
#         self._success_resp_msg_spec = None
#         self._error_resp_msg_specs = []

#     async def execute(self):
#         msg = Message(
#             self._req_msg_spec,
#             (
#                 self._entity_id,
#                 self._position.x,
#                 self._position.y,
#                 self._position.z,
#                 self._direction.x,
#                 self._direction.y,
#                 self._direction.z,
#                 self._is_on_ground,
#                 self._space_id,
#             ),
#         )
#         await self._client.send_msg(msg)
#         return CommandResult(True, None, "")


# class ForwardEntityMessageToCellappFromClientCommand(icommand.TCPCommand):
#     def __init__(
#         self, client: MsgTCPClient, entity_id: int, msgs: list[Message]
#     ) -> None:
#         super().__init__(client)
#         self._entity_id = entity_id
#         self._msgs = msgs

#         self._req_msg_spec = (
#             msgspec.baseapp.forwardEntityMessageToCellappFromClient
#         )
#         self._success_resp_msg_spec = None
#         self._error_resp_msg_specs = []

#     async def execute(self):
#         data = ENTITY_ID.encode(self._entity_id)
#         for msg in self._msgs:
#             data += MessageEncoder(msgspec.client.SPEC_BY_ID).serialize(msg)
#         envelope_msg = Message(self._req_msg_spec, (data,))
#         await self._client.send_msg(envelope_msg)
#         return CommandResult(True, None, "")


# @dataclass
# class ReqAccountBindEmailCommandResultData:
#     code: ServerError


# @dataclass
# class ReqAccountBindEmailCommandResult(CommandResult):
#     success: bool
#     result: ReqAccountBindEmailCommandResultData
#     text: str = ""


# class ReqAccountBindEmailCommand(icommand.TCPCommand):
#     def __init__(
#         self, client: MsgTCPClient, entity_id: int, password: str, email: str
#     ) -> None:
#         super().__init__(client)
#         self._entity_id = entity_id
#         self._password = password
#         self._email = email

#         self._req_msg_spec = msgspec.baseapp.reqAccountBindEmail
#         self._success_resp_msg_spec = msgspec.client.onReqAccountBindEmailCB
#         self._error_resp_msg_specs = []

#     async def execute(self) -> ReqAccountBindEmailCommandResult:
#         msg = Message(
#             self._req_msg_spec, (self._entity_id, self._password, self._email)
#         )
#         await self._client.send_msg(msg)
#         resp_msg = await self._waiting_for()
#         if resp_msg is None:
#             return ReqAccountBindEmailCommandResult(
#                 False,
#                 ReqAccountBindEmailCommandResultData(ServerError.MAX),
#                 self.get_timeout_err_text(),
#             )
#         ret_code: int = resp_msg.get_values()[0]
#         code = ServerError(ret_code)
#         if code != ServerError.SUCCESS:
#             return ReqAccountBindEmailCommandResult(
#                 False,
#                 ReqAccountBindEmailCommandResultData(ServerError.MAX),
#                 str(code),
#             )
#         return ReqAccountBindEmailCommandResult(
#             True, ReqAccountBindEmailCommandResultData(code), str(code)
#         )
