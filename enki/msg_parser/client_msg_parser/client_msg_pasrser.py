"""Обработчик сообщений для компонента Client."""

import logging
import typing
from dataclasses import dataclass
from typing import Any, ClassVar

from enki import msgspec, settings
from enki.kbeenum import ComponentType, ServerError
from enki.kbetype.decoders.basic_data_type_decoders import (
    BLOB,
    DOUBLE,
    ENTITYCALL,
    FLOAT,
    INT8,
    INT16,
    INT32,
    INT64,
    KBE_DATATYPE2ID_MAX,
    PYTHON,
    STRING,
    UINT8,
    UINT16,
    UINT32,
    UINT64,
    UNICODE,
    VECTOR2,
    VECTOR3,
    VECTOR4,
)
from enki.kbetype.decoders.custom_decoders import (
    KBEComponentType,
    KBEIntPort,
)
from enki.kbetype.pytypes.basic_data_types import KBEString, KBEUInt16
from enki.misc import devonly
from enki.msg.message import Message
from enki.msg.msg_descr import (
    MsgArgsType,
    MsgArgTypeDecoder,
    MsgDescr,
    MsgId,
    MsgLenght,
    MsgName,
)
from enki.msg_parser.imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData
from enki.net.addr import Addr, Port

logger = logging.getLogger(__name__)


@dataclass
class OnLoginSuccessfullyParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onLoginSuccessfully."""

    account_name: KBEString
    host: KBEString
    tcpPort: KBEIntPort  # noqa: N815  # pylint: disable=invalid-name
    udpPort: KBEIntPort  # noqa: N815  # pylint: disable=invalid-name
    data: bytes

    @property
    def baseapp_tcp_address(self) -> Addr:
        """Адрес для tcp соединения с хостом.

        Returns:
            Addr: TCP адрес

        """
        return Addr(
            self.host,
            Port(self.tcpPort),
        )

    @property
    def baseapp_udp_address(self) -> Addr:
        """Адрес для udp соединения с хостом.

        Returns:
            Addr: UDP адрес

        """
        return Addr(
            self.host,
            Port(self.udpPort),
        )

    __add_to_dict__: ClassVar = ("baseapp_tcp_address", "baseapp_udp_address")


@dataclass(frozen=True)
class OnLoginSuccessfullyMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onLoginSuccessfully."""

    success: bool
    result: OnLoginSuccessfullyParsedMsgData
    msg_id: int = msgspec.client.onLoginSuccessfully.id
    text: str = ""


class OnLoginSuccessfullyMsgParser(IMsgParser):
    """Парсер для Client::onLoginSuccessfully."""

    def parse(self, msg: Message) -> OnLoginSuccessfullyMsgParserResult:
        """Распарсить сообщение Client::onLoginSuccessfully.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnLoginSuccessfullyMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        account_name, offset = STRING.decode(data)
        data = data[offset:]
        host, offset = STRING.decode(data)
        data = data[offset:]
        tcp_port, offset = UINT16.decode(data)
        data = data[offset:]

        udp_port = KBEIntPort(0)
        if settings.KBE_VERSION == 2:
            udp_port, offset = UINT16.decode(data)
            data = data[offset:]

        payload_data, offset = BLOB.decode(data)
        data = data[offset:]

        pd = OnLoginSuccessfullyParsedMsgData(
            account_name, host, tcp_port, udp_port, payload_data
        )
        return OnLoginSuccessfullyMsgParserResult(success=True, result=pd)


@dataclass
class OnLoginFailedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onLoginFailed."""

    retCode: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name
    data: bytes

    @property
    def ret_code(self) -> ServerError:
        """Возвращает код ошибки в виде enum ServerError.

        Returns:
            ServerError: Код ошибки

        """
        return ServerError(self.retCode)


@dataclass(frozen=True)
class OnLoginFailedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onLoginFailed."""

    success: bool
    result: OnLoginFailedParsedMsgData
    msg_id: int = msgspec.client.onLoginFailed.id
    text: str = ""


class OnLoginFailedMsgParser(IMsgParser):
    """Парсер для Client::onLoginFailed."""

    def parse(self, msg: Message) -> OnLoginFailedMsgParserResult:
        """Распарсить сообщение Client::onLoginFailed.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnLoginFailedMsgParserResult: Результат парсинга

        """
        values: tuple[Any, ...] = msg.get_values()
        return OnLoginFailedMsgParserResult(
            success=True, result=OnLoginFailedParsedMsgData(*values)
        )


@dataclass
class OnKickedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onKicked."""

    retCode: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name

    @property
    def ret_code(self) -> ServerError:
        """Возвращает код ошибки в виде enum ServerError.

        Returns:
            ServerError: Код ошибки

        """
        return ServerError(self.retCode)


@dataclass(frozen=True)
class OnKickedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onKicked."""

    success: bool
    result: OnKickedParsedMsgData
    msg_id: int = msgspec.client.onKicked.id
    text: str = ""


class OnKickedMsgParser(IMsgParser):
    """Парсер для Client::onKicked."""

    def parse(self, msg: Message) -> OnKickedMsgParserResult:
        """Распарсить сообщение Client::onKicked.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnKickedMsgParserResult: Результат парсинга

        """
        code = msg.get_values()[0]
        code = typing.cast("KBEUInt16", code)
        return OnKickedMsgParserResult(
            success=True, result=OnKickedParsedMsgData(code)
        )


@dataclass
class OnHelloCBParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onHelloCB."""

    kbe_version: KBEString
    assets_version: KBEString
    protocol_md5: KBEString
    entity_def_md5: KBEString
    componentType: KBEComponentType  # noqa: N815  # pylint: disable=invalid-name

    @property
    def component_type(self) -> ComponentType:
        """Возвращает тип компонента в виде enum ComponentType.

        Returns:
            ComponentType: Тип компонента

        """
        return ComponentType(self.componentType)

    __add_to_dict__: ClassVar = ("component_type",)


@dataclass(frozen=True)
class OnHelloCBMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onHelloCB."""

    success: bool
    result: OnHelloCBParsedMsgData
    msg_id: int = msgspec.client.onHelloCB.id
    text: str = ""


class OnHelloCBMsgParser(IMsgParser):
    """Парсер для Client::onHelloCB."""

    def parse(self, msg: Message) -> OnHelloCBMsgParserResult:
        """Распарсить сообщение Client::onHelloCB.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnHelloCBMsgParserResult: Результат парсинга

        """
        values: tuple[Any, ...] = msg.get_values()
        return OnHelloCBMsgParserResult(
            success=True, result=OnHelloCBParsedMsgData(*values)
        )


@dataclass
class OnVersionNotMatchParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onVersionNotMatch."""

    kbe_version: KBEString


@dataclass(frozen=True)
class OnVersionNotMatchMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onVersionNotMatch."""

    success: bool
    result: OnVersionNotMatchParsedMsgData
    msg_id: int = msgspec.client.onVersionNotMatch.id
    text: str = ""


class OnVersionNotMatchMsgParser(IMsgParser):
    """Парсер для Client::onVersionNotMatch."""

    def parse(self, msg: Message) -> OnVersionNotMatchMsgParserResult:
        """Распарсить сообщение Client::onVersionNotMatch.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnVersionNotMatchMsgParserResult: Результат парсинга

        """
        values: tuple[Any, ...] = msg.get_values()
        return OnVersionNotMatchMsgParserResult(
            success=True, result=OnVersionNotMatchParsedMsgData(*values)
        )


@dataclass
class OnScriptVersionNotMatchParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onScriptVersionNotMatch."""

    assets_version: KBEString


@dataclass(frozen=True)
class OnScriptVersionNotMatchMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onScriptVersionNotMatch."""

    success: bool
    result: OnScriptVersionNotMatchParsedMsgData
    msg_id: int = msgspec.client.onScriptVersionNotMatch.id
    text: str = ""


class OnScriptVersionNotMatchMsgParser(IMsgParser):
    """Парсер для Client::onScriptVersionNotMatch."""

    def parse(self, msg: Message) -> OnScriptVersionNotMatchMsgParserResult:
        """Распарсить сообщение Client::onScriptVersionNotMatch.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnScriptVersionNotMatchMsgParserResult: Результат парсинга

        """
        values: tuple[Any, ...] = msg.get_values()
        return OnScriptVersionNotMatchMsgParserResult(
            success=True, result=OnScriptVersionNotMatchParsedMsgData(*values)
        )


@dataclass
class OnImportClientMessagesParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onImportClientMessages."""

    msg_specs: list[MsgDescr]


@dataclass(frozen=True)
class OnImportClientMessagesMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onImportClientMessages."""

    success: bool
    result: OnImportClientMessagesParsedMsgData
    msg_id: int = msgspec.client.onImportClientMessages.id
    text: str = ""


class OnImportClientMessagesMsgParser(IMsgParser):
    """Парсер для Client::onImportClientMessages."""

    # Each type has the fixed unique id in KBEngine.
    _DECODER_BY_CODE: ClassVar[dict[int, type[MsgArgTypeDecoder]]] = {
        1: STRING,
        2: UINT8,  # BOOL, DATATYPE, CHAR, DETAIL_TYPE, ENTITYCALL_CALL_TYPE
        3: UINT16,  # UNSIGNED SHORT, SERVER_ERROR_CODE, ENTITY_TYPE, ENTITY_PROPERTY_UID,
        # ENTITY_METHOD_UID, ENTITY_SCRIPT_UID, DATATYPE_UID
        4: UINT32,  # UINT, UNSIGNED INT, ARRAYSIZE, SPACE_ID, GAME_TIME, TIMER_ID
        5: UINT64,  # DBID, COMPONENT_ID
        6: INT8,
        7: INT16,  # SHORT
        8: INT32,  # INT, ENTITY_ID, CALLBACK_ID, COMPONENT_TYPE
        9: INT64,
        10: PYTHON,  # PY_DICT, PY_TUPLE, PY_LIST
        11: BLOB,
        12: UNICODE,
        13: FLOAT,
        14: DOUBLE,
        15: VECTOR2,
        16: VECTOR3,
        17: VECTOR4,
        # TODO: [2025-08-24 16:58 burov_alexey@mail.ru]:
        # Непонятно, как они могут оказаться у сообщений
        # 18: FIXED_DICT,
        # 19: ARRAY,
        20: ENTITYCALL,
        21: KBE_DATATYPE2ID_MAX,
    }

    def parse(self, msg: Message) -> OnImportClientMessagesMsgParserResult:
        """Распарсить сообщение Client::onImportClientMessages.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnImportClientMessagesMsgParserResult: Результат парсинга

        """
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])

        msg_number, offset = UINT16.decode(data)
        data = data[offset:]

        msg_specs: list[MsgDescr] = []
        while data:
            msg_id, offset = UINT16.decode(data)
            data = data[offset:]

            msg_len, offset = INT16.decode(data)
            data = data[offset:]

            msg_nam_value, offset = STRING.decode(data)
            data = data[offset:]
            msg_name = MsgName(msg_nam_value.replace("_", "::", 1))

            # MsgArgsType
            args_type, offset = INT8.decode(data)
            data = data[offset:]

            # Number of arguments
            arg_number, offset = UINT8.decode(data)
            data = data[offset:]

            arg_types: list[type[MsgArgTypeDecoder]] = []
            if arg_number > 0:
                for _ in range(arg_number):
                    code, offset = UINT8.decode(data)
                    decoder = self._DECODER_BY_CODE[code]
                    arg_types.append(decoder)
                    data = data[offset:]

            msg_specs.append(
                MsgDescr(
                    id=MsgId(msg_id),
                    lenght=MsgLenght(msg_len),
                    name=MsgName(msg_name),
                    args_type=MsgArgsType(args_type),
                    args=tuple(arg_types),
                    desc="",
                )
            )

        return OnImportClientMessagesMsgParserResult(
            success=True, result=OnImportClientMessagesParsedMsgData(msg_specs)
        )


# class _ClientAppMsgParser(IMsgParser):
#     _SAVE_MSG_TEMPL = 'There is NO entity "{entity_id}". Save the message to handle it in the future.'

#     def __init__(self, entity_helper: EntityHelper, app: App) -> None:
#         self._app = app
#         self._entity_helper = entity_helper


# class OnUpdatePropertysClientApp(_ClientApp):
#     _SAVE_MSG_TEMPL = 'There is NO entity "{entity_id}". Save the message to handle it in the future.'

#     def parse(self, msg: Message) -> OnUpdatePropertysMsgParserResult:
#         logger.debug("[%s] (%s)", self, devonly.func_args_values())
#          = OnUpdatePropertys(self._entity_helper)
#         values: tuple[Any, ...] = msg.get_values()
#         data = memoryview(values[0])
#         entity_id, data = .get_entity_id(data)

#         if not self._entity_helper.get_entity_cls_name_by_eid(entity_id):
#             self._app.add_pending_msg(entity_id, msg)
#             return OnUpdatePropertysMsgParserResult(
#                 success=False,
#                 result=OnUpdatePropertysParsedMsgData(NoValue.NO_ENTITY_ID, {}),
#                 text=self._SAVE_MSG_TEMPL.format(entity_id=entity_id),
#             )

#         return .handle(msg)


# class OnUpdatePropertysOptimizedClientApp(_ClientApp):
#     def parse(self, msg: Message) -> OnUpdatePropertysMsgParserResult:
#         logger.debug("[%s] (%s)", self, devonly.func_args_values())
#          = OnUpdatePropertysOptimized(self._entity_helper)
#         values: tuple[Any, ...] = msg.get_values()
#         data = memoryview(values[0])
#         entity_id, data = .get_entity_id(data)

#         if not self._entity_helper.get_entity_cls_name_by_eid(entity_id):
#             self._app.add_pending_msg(entity_id, msg)
#             return OnUpdatePropertysMsgParserResult(
#                 success=False,
#                 result=OnUpdatePropertysParsedMsgData(NoValue.NO_ENTITY_ID, {}),
#                 text=self._SAVE_MSG_TEMPL.format(entity_id=entity_id),
#             )

#         return .handle(msg)


# class OnCreatedProxiesClientApp(_ClientApp):
#     def parse(self, msg: Message) -> OnCreatedProxiesMsgParserResult:
#         logger.debug("[%s] (%s)", self, devonly.func_args_values())
#         res = OnCreatedProxies(self._entity_helper).handle(msg)
#         self._app.resend_pending_msgs(res.result.entity_id)
#         self._app.set_relogin_data(res.result.rnd_uuid, res.result.entity_id)
#         return res


# class OnEntityEnterWorldClientApp(_ClientApp):
#     def parse(self, msg: Message) -> OnEntityEnterWorldMsgParserResult:
#         logger.debug("[%s] %s", self, devonly.func_args_values())
#          = OnEntityEnterWorld(self._entity_helper)
#         data = msg.get_values()[0]
#         entity_id, data = .get_entity_id(data)

#         if not self._entity_helper.is_player(entity_id):
#             # The proxy entity (aka player) is initialized in the onCreatedProxies
#             self._app.resend_pending_msgs(entity_id)

#         return .handle(msg)


# _SIMPLE_TYPE_NAMES = {
#     t for t in _TYPE_NAME_BY_CODE.values() if t not in ("FIXED_DICT", "ARRAY")
# }
# _SIMPLE_TYPE_NAMES.add("PY_DICT")
# _SIMPLE_TYPE_NAMES.add("PY_TUPLE")
# _SIMPLE_TYPE_NAMES.add("PY_LIST")
