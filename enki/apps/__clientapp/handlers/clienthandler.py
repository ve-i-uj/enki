"""Обработчик сообщений для компонента Client."""

import logging
from dataclasses import dataclass
from typing import ClassVar

from enki import settings
from enki.core import kbetype, msgspec
from enki.core.message import Message
from enki.misc import devonly
from enki.net.addr import Addr

from ..ihandler import IHandler, MsgResult, ParsedMsgInfo

logger = logging.getLogger(__name__)


@dataclass
class OnLoginSuccessfullyParsedData(ParsedMsgInfo):
    """Данные распарсенного сообщения Client::onLoginSuccessfully."""

    account_name: str = ""
    host: str = ""
    tcp_port: int = 0
    udp_port: int = 0
    data: bytes = b""

    @property
    def tcp_address(self) -> Addr:
        """Адрес для tcp соединения с хостом."""
        return Addr(self.host, self.tcp_port)

    @property
    def udp_address(self) -> Addr:
        """Адрес для udp соединения с хостом."""
        return Addr(self.host, self.udp_port)

    __add_to_dict__: ClassVar = ["tcp_address", "udp_address"]


@dataclass
class OnLoginSuccessfullyHandlerResult(MsgResult):
    """Результат обработки сообщения Client::onLoginSuccessfully."""

    success: bool
    result: OnLoginSuccessfullyParsedData
    msg_id: int = msgspec.app.client.onLoginSuccessfully.id
    text: str = ""


class OnLoginSuccessfullyHandler(IHandler):
    """Обработчик для Client::onLoginSuccessfully."""

    def parse(self, msg: Message) -> OnLoginSuccessfullyMsgResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        pd = OnLoginSuccessfullyParsedData()
        pd.account_name, offset = kbetype.STRING.decode(data)
        data = data[offset:]
        pd.host, offset = kbetype.STRING.decode(data)
        data = data[offset:]
        pd.tcp_port, offset = kbetype.UINT16.decode(data)
        data = data[offset:]
        if settings.KBE_VERSION == 2:
            pd.udp_port, offset = kbetype.UINT16.decode(data)
            data = data[offset:]
        pd.data, offset = kbetype.BLOB.decode(data)
        data = data[offset:]
        return OnLoginSuccessfullyMsgResult(True, pd)


class _ClientAppMsgParser(IMsgParser):
    _SAVE_MSG_TEMPL = 'There is NO entity "{entity_id}". Save the message to handle it in the future.'

    def __init__(self, entity_helper: EntityHelper, app: App):
        self._app = app
        self._entity_helper = entity_helper


class OnUpdatePropertysClientAppHandler(_ClientAppHandler):
    _SAVE_MSG_TEMPL = 'There is NO entity "{entity_id}". Save the message to handle it in the future.'

    def parse(self, msg: Message) -> OnUpdatePropertysMsgResult:
        logger.debug(f"[{self}] ({devonly.func_args_values()})")
        handler = OnUpdatePropertysHandler(self._entity_helper)
        data: memoryview = msg.get_values()[0]
        entity_id, data = handler.get_entity_id(data)

        if not self._entity_helper.get_entity_cls_name_by_eid(entity_id):
            self._app.add_pending_msg(entity_id, msg)
            return OnUpdatePropertysMsgResult(
                success=False,
                result=OnUpdatePropertysParsedData(NoValue.NO_ENTITY_ID, {}),
                text=self._SAVE_MSG_TEMPL.format(entity_id=entity_id),
            )

        return handler.handle(msg)


class OnUpdatePropertysOptimizedClientAppHandler(_ClientAppHandler):
    def parse(self, msg: Message) -> OnUpdatePropertysMsgResult:
        logger.debug(f"[{self}] ({devonly.func_args_values()})")
        handler = OnUpdatePropertysOptimizedHandler(self._entity_helper)
        data: memoryview = msg.get_values()[0]
        entity_id, data = handler.get_entity_id(data)

        if not self._entity_helper.get_entity_cls_name_by_eid(entity_id):
            self._app.add_pending_msg(entity_id, msg)
            return OnUpdatePropertysMsgResult(
                success=False,
                result=OnUpdatePropertysParsedData(NoValue.NO_ENTITY_ID, {}),
                text=self._SAVE_MSG_TEMPL.format(entity_id=entity_id),
            )

        return handler.handle(msg)


class OnCreatedProxiesClientAppHandler(_ClientAppHandler):
    def parse(self, msg: Message) -> OnCreatedProxiesMsgResult:
        logger.debug(f"[{self}] ({devonly.func_args_values()})")
        res = OnCreatedProxiesHandler(self._entity_helper).handle(msg)
        self._app.resend_pending_msgs(res.result.entity_id)
        self._app.set_relogin_data(res.result.rnd_uuid, res.result.entity_id)
        return res


class OnEntityEnterWorldClientAppHandler(_ClientAppHandler):
    def parse(self, msg: Message) -> OnEntityEnterWorldMsgResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        handler = OnEntityEnterWorldHandler(self._entity_helper)
        data = msg.get_values()[0]
        entity_id, data = handler.get_entity_id(data)

        if not self._entity_helper.is_player(entity_id):
            # The proxy entity (aka player) is initialized in the onCreatedProxies
            self._app.resend_pending_msgs(entity_id)

        return handler.handle(msg)


@dataclass
class OnKickedHandlerParsedData(ParsedMsgInfo):
    ret_code: ServerError


@dataclass
class OnKickedHandlerResult(MsgResult):
    success: bool
    result: OnKickedHandlerParsedData
    msg_id: int = msgspec.app.client.onKicked.id
    text: str = ""


class OnKickedMsgParser(IMsgParser):
    def __init__(self, app: IApp) -> None:
        super().__init__()
        self._app = app

    def parse(self, msg: Message) -> OnKickedMsgResult:
        code: int = msg.get_values()[0]
        server_error = ServerError(code)
        return OnKickedMsgResult(True, OnKickedHandlerParsedData(server_error))


CLIENT_HANDLERS: dict[int, Type[Handler]] = {
    msgspec.app.client.onLoginSuccessfully.id: OnLoginSuccessfullyHandler
}
