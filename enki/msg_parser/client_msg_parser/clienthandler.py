"""Обработчик сообщений для компонента Client."""

import logging
from dataclasses import dataclass
from typing import ClassVar

from enki import settings
from enki.core import kbetype, msgspec
from enki.core.message import Message
from enki.misc import devonly
from enki.msg_parser.ihandler import IHandler, MsgResult, ParsedMsgInfo
from enki.net.addr import Addr

logger = logging.getLogger(__name__)


@dataclass
class OnLoginSuccessfullyParsedMsgData(ParsedMsgInfo):
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
class OnLoginSuccessfullyMsgParserResult(MsgResult):
    """Результат обработки сообщения Client::onLoginSuccessfully."""

    success: bool
    result: OnLoginSuccessfullyParsedMsgData
    msg_id: int = msgspec.client.onLoginSuccessfully.id
    text: str = ""


class OnLoginSuccessfullyHandler(IHandler):
    """Парсер для Client::onLoginSuccessfully."""

    def parse(self, msg: Message) -> OnLoginSuccessfullyMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        pd = OnLoginSuccessfullyParsedMsgData()
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
        return OnLoginSuccessfullyMsgParserResult(True, pd)


class _ClientAppMsgParser(IMsgParser):
    _SAVE_MSG_TEMPL = 'There is NO entity "{entity_id}". Save the message to handle it in the future.'

    def __init__(self, entity_helper: EntityHelper, app: App) -> None:
        self._app = app
        self._entity_helper = entity_helper


class OnUpdatePropertysClientAppHandler(_ClientAppHandler):
    _SAVE_MSG_TEMPL = 'There is NO entity "{entity_id}". Save the message to handle it in the future.'

    def parse(self, msg: Message) -> OnUpdatePropertysMsgParserResult:
        logger.debug("[%s] (%s)", self, devonly.func_args_values())
        handler = OnUpdatePropertysHandler(self._entity_helper)
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        entity_id, data = handler.get_entity_id(data)

        if not self._entity_helper.get_entity_cls_name_by_eid(entity_id):
            self._app.add_pending_msg(entity_id, msg)
            return OnUpdatePropertysMsgParserResult(
                success=False,
                result=OnUpdatePropertysParsedMsgData(NoValue.NO_ENTITY_ID, {}),
                text=self._SAVE_MSG_TEMPL.format(entity_id=entity_id),
            )

        return handler.handle(msg)


class OnUpdatePropertysOptimizedClientAppHandler(_ClientAppHandler):
    def parse(self, msg: Message) -> OnUpdatePropertysMsgParserResult:
        logger.debug("[%s] (%s)", self, devonly.func_args_values())
        handler = OnUpdatePropertysOptimizedHandler(self._entity_helper)
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        entity_id, data = handler.get_entity_id(data)

        if not self._entity_helper.get_entity_cls_name_by_eid(entity_id):
            self._app.add_pending_msg(entity_id, msg)
            return OnUpdatePropertysMsgParserResult(
                success=False,
                result=OnUpdatePropertysParsedMsgData(NoValue.NO_ENTITY_ID, {}),
                text=self._SAVE_MSG_TEMPL.format(entity_id=entity_id),
            )

        return handler.handle(msg)


class OnCreatedProxiesClientAppHandler(_ClientAppHandler):
    def parse(self, msg: Message) -> OnCreatedProxiesMsgParserResult:
        logger.debug("[%s] (%s)", self, devonly.func_args_values())
        res = OnCreatedProxiesHandler(self._entity_helper).handle(msg)
        self._app.resend_pending_msgs(res.result.entity_id)
        self._app.set_relogin_data(res.result.rnd_uuid, res.result.entity_id)
        return res


class OnEntityEnterWorldClientAppHandler(_ClientAppHandler):
    def parse(self, msg: Message) -> OnEntityEnterWorldMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        handler = OnEntityEnterWorldHandler(self._entity_helper)
        data = msg.get_values()[0]
        entity_id, data = handler.get_entity_id(data)

        if not self._entity_helper.is_player(entity_id):
            # The proxy entity (aka player) is initialized in the onCreatedProxies
            self._app.resend_pending_msgs(entity_id)

        return handler.handle(msg)


@dataclass
class OnKickedHandlerParsedMsgData(ParsedMsgInfo):
    ret_code: ServerError


@dataclass
class OnKickedMsgParserResult(MsgResult):
    success: bool
    result: OnKickedHandlerParsedMsgData
    msg_id: int = msgspec.client.onKicked.id
    text: str = ""


class OnKickedMsgParser(IMsgParser):
    def __init__(self, app: IApp) -> None:
        super().__init__()
        self._app = app

    def parse(self, msg: Message) -> OnKickedMsgParserResult:
        code: int = msg.get_values()[0]
        server_error = ServerError(code)
        return OnKickedMsgParserResult(
            True, OnKickedHandlerParsedMsgData(server_error)
        )


CLIENT_HANDLERS: dict[int, Type[Handler]] = {
    msgspec.client.onLoginSuccessfully.id: OnLoginSuccessfullyHandler
}
