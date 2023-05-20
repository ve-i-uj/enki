"""Commands for sending messages to BaseApp."""

import logging
from dataclasses import dataclass
from typing import List, Tuple, Optional

from enki.core.enkitype import NoValue
from enki import settings
from enki.core import msgspec
from enki.core.kbeenum import ServerError
from enki.core import kbetype
from enki.core.message import Message, MsgDescr, MessageSerializer
from enki.core.kbetype import Position, Direction
from enki.net.client import TCPClient

from . import _base
from ._base import CommandResult


logger = logging.getLogger(__name__)


@dataclass
class ImportClientMessagesParsedData:
    data: memoryview


class ImportClientMessagesCommandResult(CommandResult):
    success: bool
    result: ImportClientMessagesParsedData
    text: str = ''


class ImportClientMessagesCommand(_base.TCPCommand):
    """BaseApp command 'importClientMessages'."""

    def __init__(self, client: TCPClient):
        super().__init__(client)

        self._req_msg_spec: MsgDescr = msgspec.app.baseapp.importClientMessages
        self._success_resp_msg_spec: MsgDescr = msgspec.app.client.onImportClientMessages
        self._error_resp_msg_specs: List[MsgDescr] = []

        self._msg = Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> ImportClientMessagesCommandResult:
        await self._client.send_msg(self._msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            return ImportClientMessagesCommandResult(
                False, text=self.get_timeout_err_text()
            )

        data: memoryview = resp_msg.get_values()[0]
        return ImportClientMessagesCommandResult(
            True, ImportClientMessagesParsedData(data)
        )


class ImportClientEntityDefCommand(_base.TCPCommand):
    """BaseApp command 'importClientEntityDef'."""

    def __init__(self, client: TCPClient):
        super().__init__(client)

        self._req_msg_spec: MsgDescr = msgspec.app.baseapp.importClientEntityDef
        self._success_resp_msg_spec: MsgDescr = msgspec.app.client.onImportClientEntityDef
        self._error_resp_msg_specs: List[MsgDescr] = []

        self._msg = Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> memoryview:
        await self._client.send_msg(self._msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            logger.error(_base.TIMEOUT_ERROR_MSG)
            return memoryview(b'')
        data = resp_msg.get_values()[0]
        return data


class HelloCommand(_base.TCPCommand):
    """BaseApp command 'hello'."""

    def __init__(self, kbe_version: str, script_version: str, encrypted_key: bytes,
                 client: TCPClient):
        super().__init__(client)

        self._req_msg_spec: MsgDescr = msgspec.app.baseapp.hello
        self._success_resp_msg_spec: MsgDescr = msgspec.app.client.onHelloCB
        self._error_resp_msg_specs: List[MsgDescr] = [
            msgspec.app.client.onVersionNotMatch,
            msgspec.app.client.onScriptVersionNotMatch,
        ]

        self._msg = Message(
            spec=self._req_msg_spec,
            fields=(kbe_version, script_version, encrypted_key)
        )

    async def execute(self) -> CommandResult:
        await self._client.send_msg(self._msg)
        resp_msg = await self._waiting_for(settings.WAITING_FOR_SERVER_TIMEOUT)
        if resp_msg is None:
            return CommandResult(False, text=self.get_timeout_err_text())

        if resp_msg.id == msgspec.app.client.onVersionNotMatch.id:
            kbe_version = self._msg.get_values()[0]
            data: memoryview = resp_msg.get_values()[0]
            actual_kbe_version, offset = kbetype.STRING.decode(data)
            data = data[offset:]
            msg = f'Plugin designed for KBEngine version "{kbe_version}". ' \
                  f'But actual KBEngine version is "{actual_kbe_version}"'
            return CommandResult(False, msg)

        if resp_msg.id == msgspec.app.client.onScriptVersionNotMatch.id:
            script_version = self._msg.get_values()[1]
            data: memoryview = resp_msg.get_values()[0]
            actual_script_version, offset = kbetype.STRING.decode(data)
            data = data[offset:]
            msg = f'Plugin designed for script version "{script_version}". ' \
                  f'But actual script version is "{actual_script_version}"'
            return CommandResult(False, msg)

        return CommandResult(True, '')


class OnClientActiveTickCommand(_base.TCPCommand):
    """BaseApp command 'onClientActiveTick'."""

    def __init__(self, client: TCPClient,
                 timeout: float = 0.0):
        super().__init__(client)

        self._req_msg_spec: MsgDescr = msgspec.app.baseapp.onClientActiveTick
        self._success_resp_msg_spec: MsgDescr = msgspec.app.client.onAppActiveTickCB
        self._error_resp_msg_specs: List[MsgDescr] = []

        self._timeout = timeout
        self._msg = Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> CommandResult:
        await self._client.send_msg(self._msg)
        resp_msg = await self._waiting_for(self._timeout)
        if resp_msg is None:
            return CommandResult(
                False, f'No response for the "{self._req_msg_spec.name}"'
            )

        return CommandResult(True)


class LoginBaseappCommand(_base.TCPCommand):

    def __init__(self, client: TCPClient, account_name: str, password: str):
        super().__init__(client)
        self._account_name = account_name
        self._password = password

        self._req_msg_spec = msgspec.app.baseapp.loginBaseapp
        self._success_resp_msg_spec = None
        self._error_resp_msg_specs = [msgspec.app.client.onLoginBaseappFailed]

    async def execute(self) -> CommandResult:
        msg = Message(
            msgspec.app.baseapp.loginBaseapp, (self._account_name, self._password)
        )
        await self._client.send_msg(msg)
        resp_msg = await self._waiting_for()
        if resp_msg is None:
            # Good. There were no error messages.
            return CommandResult(True, '')
        err_code = resp_msg.get_values()[0]
        err_name = ServerError(err_code).name
        text = f'The client cannot connect to the BaseApp ({err_name})'
        return CommandResult(False, text)


@dataclass
class ReloginBaseappCommandResultData:
    rnd_uuid: int = NoValue.NO_ID


@dataclass
class ReloginBaseappCommandResult(CommandResult):
    success: bool
    result: ReloginBaseappCommandResultData
    text: str = ''


class ReloginBaseappCommand(_base.TCPCommand):

    def __init__(self, account_name: str, password: str, rnd_uuid: int,
                 entity_id: int, client: TCPClient, ):
        super().__init__(client)
        self._account_name = account_name
        self._password = password
        self._rnd_uuid = rnd_uuid
        self._entity_id = entity_id

        self._req_msg_spec = msgspec.app.baseapp.reloginBaseapp
        self._success_resp_msg_spec: MsgDescr = msgspec.app.client.onReloginBaseappSuccessfully
        self._error_resp_msg_specs = [msgspec.app.client.onReloginBaseappFailed]

    async def execute(self) -> ReloginBaseappCommandResult:
        msg = Message(
            self._req_msg_spec,
            (self._account_name, self._password, self._rnd_uuid, self._entity_id)
        )
        await self._client.send_msg(msg)
        resp_msg = await self._waiting_for()
        if resp_msg is None:
            return ReloginBaseappCommandResult(
                False,
                ReloginBaseappCommandResultData(),
                self.get_timeout_err_text()
            )

        if resp_msg.id in [s.id for s in self._error_resp_msg_specs]:
            err_code: int = resp_msg.get_values()[0]
            err_text = ServerError(err_code).name
            return ReloginBaseappCommandResult(
                False,
                ReloginBaseappCommandResultData(),
                f'It cannot relogin to the BaseApp ({err_text})'
            )

        rnd_uuid: int = resp_msg.get_values()[0]
        return ReloginBaseappCommandResult(True, ReloginBaseappCommandResultData(rnd_uuid))


@dataclass
class ReqAccountNewPasswordCommandResultData:
    code: ServerError


@dataclass
class ReqAccountNewPasswordResult(CommandResult):
    success: bool
    result: ReqAccountNewPasswordCommandResultData
    text: str = ''


class ReqAccountNewPasswordCommand(_base.TCPCommand):

    def __init__(self, client: TCPClient, entity_id: int, old_pwd: str, new_pwd: str):
        super().__init__(client)
        self._entity_id = entity_id
        self._old_pwd = old_pwd
        self._new_pwd = new_pwd

        self._req_msg_spec = msgspec.app.baseapp.reqAccountNewPassword
        self._success_resp_msg_spec: MsgDescr = msgspec.app.client.onReqAccountNewPasswordCB
        self._error_resp_msg_specs = []

    async def execute(self) -> ReqAccountNewPasswordResult:
        msg = Message(
            self._req_msg_spec,
            (self._entity_id, self._old_pwd, self._new_pwd)
        )
        await self._client.send_msg(msg)
        resp_msg = await self._waiting_for()
        if resp_msg is None:
            return ReqAccountNewPasswordResult(
                False,
                text=self.get_timeout_err_text()
            )

        # It's the "onReqAccountNewPasswordCB" message because no answer if something's wrong.
        ret_code: int = resp_msg.get_values()[0]
        if ServerError(ret_code) != ServerError.SUCCESS:
            return ReqAccountNewPasswordResult(
                False,
                text=ServerError(ret_code).name
            )
        return ReqAccountNewPasswordResult(
            True,
            ReqAccountNewPasswordCommandResultData(ServerError(ret_code))
        )


class LogoutBaseappCommand(_base.TCPCommand):
    """The client connection will be closed by the server after this command executes."""

    def __init__(self, client: TCPClient, rnd_uuid: int, entity_id: int):
        super().__init__(client)
        self._rnd_uuid = rnd_uuid
        self._entity_id = entity_id

        self._req_msg_spec = msgspec.app.baseapp.logoutBaseapp
        self._success_resp_msg_spec = None
        self._error_resp_msg_specs = []

    async def execute(self):
        msg = Message(
            self._req_msg_spec,
            (self._rnd_uuid, self._entity_id)
        )
        await self._client.send_msg(msg)
        return CommandResult(True, None, '')


class OnUpdateDataFromClientCommand(_base.TCPCommand):

    def __init__(self, client: TCPClient, position: Position,
                 direction: Direction, is_on_ground: bool,
                 space_id: int):
        super().__init__(client)
        self._position = position
        self._direction = direction
        self._is_on_ground = is_on_ground
        self._space_id = space_id

        self._req_msg_spec = msgspec.app.baseapp.onUpdateDataFromClient
        self._success_resp_msg_spec = None
        self._error_resp_msg_specs = []

    async def execute(self):
        msg = Message(
            self._req_msg_spec,
            (self._position.x, self._position.y, self._position.z,
             self._direction.x, self._direction.y, self._direction.z,
             self._is_on_ground, self._space_id)
        )
        await self._client.send_msg(msg)
        # The "onUpdateBasePos" message only will be sent to the client in
        # the server messages. The response mush be handled in the application
        # handler because there is no direct responses for this request.
        return CommandResult(True, None, '')


class OnUpdateDataFromClientForControlledEntityCommand(_base.TCPCommand):

    def __init__(self, client: TCPClient, entity_id: int,
                 position: Position, direction: Direction,
                 is_on_ground: bool, space_id: int):
        super().__init__(client)
        self._entity_id = entity_id
        self._position = position
        self._direction = direction
        self._is_on_ground = is_on_ground
        self._space_id = space_id

        self._req_msg_spec = msgspec.app.baseapp.onUpdateDataFromClientForControlledEntity
        self._success_resp_msg_spec = None
        self._error_resp_msg_specs = []

    async def execute(self):
        msg = Message(
            self._req_msg_spec,
            (self._entity_id, self._position.x, self._position.y, self._position.z,
             self._direction.x, self._direction.y, self._direction.z,
             self._is_on_ground, self._space_id)
        )
        await self._client.send_msg(msg)
        return CommandResult(True, None, '')


class ForwardEntityMessageToCellappFromClientCommand(_base.TCPCommand):

    def __init__(self, client: TCPClient, entity_id: int, msgs: list[Message]):
        super().__init__(client)
        self._entity_id = entity_id
        self._msgs = msgs

        self._req_msg_spec = msgspec.app.baseapp.forwardEntityMessageToCellappFromClient
        self._success_resp_msg_spec = None
        self._error_resp_msg_specs = []

    async def execute(self):
        data = kbetype.ENTITY_ID.encode(self._entity_id)
        for msg in self._msgs:
            data += MessageSerializer(msgspec.app.client.SPEC_BY_ID).serialize(msg)
        envelope_msg = Message(
            self._req_msg_spec, (data, )
        )
        await self._client.send_msg(envelope_msg)
        return CommandResult(True, None, '')


@dataclass
class ReqAccountBindEmailCommandResultData:
    code: ServerError


@dataclass
class ReqAccountBindEmailCommandResult(CommandResult):
    success: bool
    result: ReqAccountBindEmailCommandResultData
    text: str = ''


class ReqAccountBindEmailCommand(_base.TCPCommand):

    def __init__(self, client: TCPClient, entity_id: int, password: str, email: str):
        super().__init__(client)
        self._entity_id = entity_id
        self._password = password
        self._email = email

        self._req_msg_spec = msgspec.app.baseapp.reqAccountBindEmail
        self._success_resp_msg_spec = msgspec.app.client.onReqAccountBindEmailCB
        self._error_resp_msg_specs = []

    async def execute(self) -> ReqAccountBindEmailCommandResult:
        msg = Message(
            self._req_msg_spec,
            (self._entity_id, self._password, self._email)
        )
        await self._client.send_msg(msg)
        resp_msg = await self._waiting_for()
        if resp_msg is None:
            return ReqAccountBindEmailCommandResult(
                False,
                ReqAccountBindEmailCommandResultData(ServerError.MAX),
                self.get_timeout_err_text()
            )
        ret_code: int = resp_msg.get_values()[0]
        code = ServerError(ret_code)
        if code != ServerError.SUCCESS:
            return ReqAccountBindEmailCommandResult(
                False,
                ReqAccountBindEmailCommandResultData(ServerError.MAX),
                str(code)
            )
        return ReqAccountBindEmailCommandResult(
            True,
            ReqAccountBindEmailCommandResultData(code),
            str(code)
        )
