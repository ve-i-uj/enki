"""Обработчик сообщений для компонента Client."""

from __future__ import annotations

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
    KBEEntityId,
    KBEEntityTypeName,
    KBEIntPort,
    KBEServerErrorCode,
)
from enki.kbetype.pytypes.basic_data_types import (
    KBEBlob,
    KBERowByteData,
    KBEString,
    KBEUInt16,
    KBEUInt32,
    KBEUInt64,
)
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
from enki.msg_parser.imsg_parser import (
    IMsgParser,
    MsgParserResult,
    ParsedMsgData,
)
from enki.net.addr import Addr, Port

if typing.TYPE_CHECKING:
    from enki.msg.message import Message

logger = logging.getLogger(__name__)


@dataclass
class OnLoginSuccessfullyParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onLoginSuccessfully."""

    account_name: KBEString
    host: KBEString
    tcpPort: KBEIntPort  # noqa: N815  # pylint: disable=invalid-name
    udpPort: KBEIntPort  # noqa: N815  # pylint: disable=invalid-name
    data: KBEBlob

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
    data: KBEBlob

    @property
    def ret_code(self) -> ServerError:
        """Возвращает код ошибки в виде enum ServerError.

        Returns:
            ServerError: Код ошибки

        """
        return ServerError(self.retCode)

    __add_to_dict__: ClassVar = ("ret_code",)


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
    componentType: KBEComponentType  # pylint: disable=invalid-name

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

        _msg_number, offset = UINT16.decode(data)
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


@dataclass
class OnUpdatePropertysParsedMsgData(ParsedMsgData):
    entity_id: KBEEntityId
    entity_data: KBERowByteData


@dataclass(frozen=True)
class OnUpdatePropertysMsgParserResult(MsgParserResult):
    success: bool
    result: OnUpdatePropertysParsedMsgData | None
    msg_id: int = msgspec.client.onUpdatePropertys.id
    text: str = ""


class OnUpdatePropertysMsgParser(IMsgParser):
    """Парсер для Client::onUpdatePropertys."""

    def parse(self, msg: Message) -> OnUpdatePropertysMsgParserResult:
        logger.debug("[%s] (%s)", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnUpdatePropertysParsedMsgData(*values)

        return OnUpdatePropertysMsgParserResult(success=True, result=pd)


@dataclass
class OnCreatedProxiesParsedMsgData(ParsedMsgData):
    rnd_uuid: KBEUInt64  # rndUUID
    entity_id: KBEEntityId  # eid
    entity_type: KBEEntityTypeName  # entityType


@dataclass(frozen=True)
class OnCreatedProxiesMsgParserResult(MsgParserResult):
    success: bool
    result: OnCreatedProxiesParsedMsgData | None
    msg_id: int = msgspec.client.onCreatedProxies.id
    text: str = ""


class OnCreatedProxiesMsgParser(IMsgParser):
    """Парсер для Client::onCreatedProxies."""

    def parse(self, msg: Message) -> OnCreatedProxiesMsgParserResult:
        logger.debug("[%s] (%s)", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnCreatedProxiesParsedMsgData(*values)

        return OnCreatedProxiesMsgParserResult(success=True, result=pd)


@dataclass
class OnAppActiveTickCBParsedMsgData(ParsedMsgData):
    """Данные парсинга Client::onAppActiveTickCB."""


@dataclass(frozen=True)
class OnAppActiveTickCBMsgParserResult(MsgParserResult):
    """Результат парсинга Client::onAppActiveTickCB."""

    success: bool
    result: OnAppActiveTickCBParsedMsgData
    msg_id: int = msgspec.client.onAppActiveTickCB.id
    text: str = ""


class OnAppActiveTickCBMsgParser(IMsgParser):
    """Парсер для Client::onAppActiveTickCB."""

    def parse(self, msg: Message) -> OnAppActiveTickCBMsgParserResult:
        """Парсинг сообщения Client::onAppActiveTickCB.

        :param msg: Сообщение для парсинга
        :return: Результат парсинга
        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        # Сообщение не имеет аргументов, просто возвращаем пустые данные
        return OnAppActiveTickCBMsgParserResult(
            success=True, result=OnAppActiveTickCBParsedMsgData()
        )


@dataclass
class OnReloginBaseappFailedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onReloginBaseappFailed."""

    retCode: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name

    @property
    def ret_code(self) -> ServerError:
        """Возвращает код ошибки в виде enum ServerError.

        Returns:
            ServerError: Код ошибки

        """
        return ServerError(self.retCode)

    __add_to_dict__: ClassVar = ("ret_code",)


@dataclass(frozen=True)
class OnReloginBaseappFailedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onReloginBaseappFailed."""

    success: bool
    result: OnReloginBaseappFailedParsedMsgData
    msg_id: int = msgspec.client.onReloginBaseappFailed.id
    text: str = ""


class OnReloginBaseappFailedMsgParser(IMsgParser):
    """Парсер для Client::onReloginBaseappFailed."""

    def parse(self, msg: Message) -> OnReloginBaseappFailedMsgParserResult:
        """Распарсить сообщение Client::onReloginBaseappFailed.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnReloginBaseappFailedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        code = values[0]
        return OnReloginBaseappFailedMsgParserResult(
            success=True, result=OnReloginBaseappFailedParsedMsgData(code)
        )


@dataclass
class OnEntityLeaveWorldOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onEntityLeaveWorldOptimized."""

    entity_data: KBERowByteData


@dataclass(frozen=True)
class OnEntityLeaveWorldOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onEntityLeaveWorldOptimized."""

    success: bool
    result: OnEntityLeaveWorldOptimizedParsedMsgData
    msg_id: int = msgspec.client.onEntityLeaveWorldOptimized.id
    text: str = ""


class OnEntityLeaveWorldOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onEntityLeaveWorldOptimized."""

    def parse(self, msg: Message) -> OnEntityLeaveWorldOptimizedMsgParserResult:
        """Распарсить сообщение Client::onEntityLeaveWorldOptimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnEntityLeaveWorldOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnEntityLeaveWorldOptimizedMsgParserResult(
            success=True, result=OnEntityLeaveWorldOptimizedParsedMsgData(data)
        )


@dataclass
class OnRemoteMethodCallOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onRemoteMethodCallOptimized."""

    method_data: KBERowByteData


@dataclass(frozen=True)
class OnRemoteMethodCallOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onRemoteMethodCallOptimized."""

    success: bool
    result: OnRemoteMethodCallOptimizedParsedMsgData
    msg_id: int = msgspec.client.onRemoteMethodCallOptimized.id
    text: str = ""


class OnRemoteMethodCallOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onRemoteMethodCallOptimized."""

    def parse(self, msg: Message) -> OnRemoteMethodCallOptimizedMsgParserResult:
        """Распарсить сообщение Client::onRemoteMethodCallOptimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnRemoteMethodCallOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnRemoteMethodCallOptimizedMsgParserResult(
            success=True, result=OnRemoteMethodCallOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdatePropertysOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdatePropertysOptimized."""

    property_data: KBERowByteData


@dataclass(frozen=True)
class OnUpdatePropertysOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdatePropertysOptimized."""

    success: bool
    result: OnUpdatePropertysOptimizedParsedMsgData
    msg_id: int = msgspec.client.onUpdatePropertysOptimized.id
    text: str = ""


class OnUpdatePropertysOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdatePropertysOptimized."""

    def parse(self, msg: Message) -> OnUpdatePropertysOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdatePropertysOptimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdatePropertysOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdatePropertysOptimizedMsgParserResult(
            success=True, result=OnUpdatePropertysOptimizedParsedMsgData(data)
        )


@dataclass
class OnSetEntityPosAndDirParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onSetEntityPosAndDir."""

    position_data: KBERowByteData


@dataclass(frozen=True)
class OnSetEntityPosAndDirMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onSetEntityPosAndDir."""

    success: bool
    result: OnSetEntityPosAndDirParsedMsgData
    msg_id: int = msgspec.client.onSetEntityPosAndDir.id
    text: str = ""


class OnSetEntityPosAndDirMsgParser(IMsgParser):
    """Парсер для Client::onSetEntityPosAndDir."""

    def parse(self, msg: Message) -> OnSetEntityPosAndDirMsgParserResult:
        """Распарсить сообщение Client::onSetEntityPosAndDir.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnSetEntityPosAndDirMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnSetEntityPosAndDirMsgParserResult(
            success=True, result=OnSetEntityPosAndDirParsedMsgData(data)
        )


@dataclass
class OnUpdateBasePosParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateBasePos."""

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class OnUpdateBasePosMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateBasePos."""

    success: bool
    result: OnUpdateBasePosParsedMsgData
    msg_id: int = msgspec.client.onUpdateBasePos.id
    text: str = ""


class OnUpdateBasePosMsgParser(IMsgParser):
    """Парсер для Client::onUpdateBasePos."""

    def parse(self, msg: Message) -> OnUpdateBasePosMsgParserResult:
        """Распарсить сообщение Client::onUpdateBasePos.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateBasePosMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        return OnUpdateBasePosMsgParserResult(
            success=True, result=OnUpdateBasePosParsedMsgData(*values)
        )


@dataclass
class OnUpdateBaseDirParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateBaseDir."""

    direction_data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateBaseDirMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateBaseDir."""

    success: bool
    result: OnUpdateBaseDirParsedMsgData
    msg_id: int = msgspec.client.onUpdateBaseDir.id
    text: str = ""


class OnUpdateBaseDirMsgParser(IMsgParser):
    """Парсер для Client::onUpdateBaseDir."""

    def parse(self, msg: Message) -> OnUpdateBaseDirMsgParserResult:
        """Распарсить сообщение Client::onUpdateBaseDir.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateBaseDirMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateBaseDirMsgParserResult(
            success=True, result=OnUpdateBaseDirParsedMsgData(data)
        )


@dataclass
class OnUpdateBasePosXZParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateBasePosXZ."""

    x: float
    z: float


@dataclass(frozen=True)
class OnUpdateBasePosXZMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateBasePosXZ."""

    success: bool
    result: OnUpdateBasePosXZParsedMsgData
    msg_id: int = msgspec.client.onUpdateBasePosXZ.id
    text: str = ""


class OnUpdateBasePosXZMsgParser(IMsgParser):
    """Парсер для Client::onUpdateBasePosXZ."""

    def parse(self, msg: Message) -> OnUpdateBasePosXZMsgParserResult:
        """Распарсить сообщение Client::onUpdateBasePosXZ.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateBasePosXZMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        return OnUpdateBasePosXZMsgParserResult(
            success=True, result=OnUpdateBasePosXZParsedMsgData(*values)
        )


@dataclass
class OnUpdateDataParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData."""

    update_data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData."""

    success: bool
    result: OnUpdateDataParsedMsgData
    msg_id: int = msgspec.client.onUpdateData.id
    text: str = ""


class OnUpdateDataMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData."""

    def parse(self, msg: Message) -> OnUpdateDataMsgParserResult:
        """Распарсить сообщение Client::onUpdateData.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataMsgParserResult(
            success=True, result=OnUpdateDataParsedMsgData(data)
        )


@dataclass
class OnEntityLeaveWorldParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onEntityLeaveWorld."""

    entity_id: int


@dataclass(frozen=True)
class OnEntityLeaveWorldMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onEntityLeaveWorld."""

    success: bool
    result: OnEntityLeaveWorldParsedMsgData
    msg_id: int = msgspec.client.onEntityLeaveWorld.id
    text: str = ""


class OnEntityLeaveWorldMsgParser(IMsgParser):
    """Парсер для Client::onEntityLeaveWorld."""

    def parse(self, msg: Message) -> OnEntityLeaveWorldMsgParserResult:
        """Распарсить сообщение Client::onEntityLeaveWorld.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnEntityLeaveWorldMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        entity_id = values[0]
        return OnEntityLeaveWorldMsgParserResult(
            success=True, result=OnEntityLeaveWorldParsedMsgData(entity_id)
        )


@dataclass
class OnEntityDestroyedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onEntityDestroyed."""

    entity_id: int


@dataclass(frozen=True)
class OnEntityDestroyedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onEntityDestroyed."""

    success: bool
    result: OnEntityDestroyedParsedMsgData
    msg_id: int = msgspec.client.onEntityDestroyed.id
    text: str = ""


class OnEntityDestroyedMsgParser(IMsgParser):
    """Парсер для Client::onEntityDestroyed."""

    def parse(self, msg: Message) -> OnEntityDestroyedMsgParserResult:
        """Распарсить сообщение Client::onEntityDestroyed.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnEntityDestroyedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        entity_id = values[0]
        return OnEntityDestroyedMsgParserResult(
            success=True, result=OnEntityDestroyedParsedMsgData(entity_id)
        )


@dataclass
class OnStreamDataCompletedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onStreamDataCompleted."""

    stream_id: int


@dataclass(frozen=True)
class OnStreamDataCompletedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onStreamDataCompleted."""

    success: bool
    result: OnStreamDataCompletedParsedMsgData
    msg_id: int = msgspec.client.onStreamDataCompleted.id
    text: str = ""


class OnStreamDataCompletedMsgParser(IMsgParser):
    """Парсер для Client::onStreamDataCompleted."""

    def parse(self, msg: Message) -> OnStreamDataCompletedMsgParserResult:
        """Распарсить сообщение Client::onStreamDataCompleted.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnStreamDataCompletedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        stream_id = values[0]
        return OnStreamDataCompletedMsgParserResult(
            success=True, result=OnStreamDataCompletedParsedMsgData(stream_id)
        )


@dataclass
class OnLoginBaseappFailedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onLoginBaseappFailed."""

    retCode: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name

    @property
    def ret_code(self) -> ServerError:
        """Возвращает код ошибки в виде enum ServerError.

        Returns:
            ServerError: Код ошибки

        """
        return ServerError(self.retCode)

    __add_to_dict__: ClassVar = ("ret_code",)


@dataclass(frozen=True)
class OnLoginBaseappFailedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onLoginBaseappFailed."""

    success: bool
    result: OnLoginBaseappFailedParsedMsgData
    msg_id: int = msgspec.client.onLoginBaseappFailed.id
    text: str = ""


class OnLoginBaseappFailedMsgParser(IMsgParser):
    """Парсер для Client::onLoginBaseappFailed."""

    def parse(self, msg: Message) -> OnLoginBaseappFailedMsgParserResult:
        """Распарсить сообщение Client::onLoginBaseappFailed.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnLoginBaseappFailedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        code = values[0]
        return OnLoginBaseappFailedMsgParserResult(
            success=True, result=OnLoginBaseappFailedParsedMsgData(code)
        )


@dataclass
class OnControlEntityParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onControlEntity."""

    entity_id: int
    control_type: int


@dataclass(frozen=True)
class OnControlEntityMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onControlEntity."""

    success: bool
    result: OnControlEntityParsedMsgData
    msg_id: int = msgspec.client.onControlEntity.id
    text: str = ""


class OnControlEntityMsgParser(IMsgParser):
    """Парсер для Client::onControlEntity."""

    def parse(self, msg: Message) -> OnControlEntityMsgParserResult:
        """Распарсить сообщение Client::onControlEntity.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnControlEntityMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        entity_id, control_type = values
        return OnControlEntityMsgParserResult(
            success=True,
            result=OnControlEntityParsedMsgData(entity_id, control_type),
        )


@dataclass
class SetSpaceDataParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::setSpaceData."""

    space_id: KBEUInt32
    key: KBEString
    value: KBEString


@dataclass(frozen=True)
class SetSpaceDataMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::setSpaceData."""

    success: bool
    result: SetSpaceDataParsedMsgData
    msg_id: int = msgspec.client.setSpaceData.id
    text: str = ""


class SetSpaceDataMsgParser(IMsgParser):
    """Парсер для Client::setSpaceData."""

    def parse(self, msg: Message) -> SetSpaceDataMsgParserResult:
        """Распарсить сообщение Client::setSpaceData.

        Args:
            msg: Сообщение для парсинга

        Returns:
            SetSpaceDataMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        return SetSpaceDataMsgParserResult(
            success=True, result=SetSpaceDataParsedMsgData(*values)
        )


@dataclass
class DelSpaceDataParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::delSpaceData."""

    space_id: KBEUInt32
    key: KBEString


@dataclass(frozen=True)
class DelSpaceDataMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::delSpaceData."""

    success: bool
    result: DelSpaceDataParsedMsgData
    msg_id: int = msgspec.client.delSpaceData.id
    text: str = ""


class DelSpaceDataMsgParser(IMsgParser):
    """Парсер для Client::delSpaceData."""

    def parse(self, msg: Message) -> DelSpaceDataMsgParserResult:
        """Распарсить сообщение Client::delSpaceData.

        Args:
            msg: Сообщение для парсинга

        Returns:
            DelSpaceDataMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        return DelSpaceDataMsgParserResult(
            success=True, result=DelSpaceDataParsedMsgData(*values)
        )


@dataclass
class OnReqAccountResetPasswordCBParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onReqAccountResetPasswordCB."""

    retCode: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name

    @property
    def ret_code(self) -> ServerError:
        """Возвращает код ошибки в виде enum ServerError.

        Returns:
            ServerError: Код ошибки

        """
        return ServerError(self.retCode)

    __add_to_dict__: ClassVar = ("ret_code",)


@dataclass(frozen=True)
class OnReqAccountResetPasswordCBMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onReqAccountResetPasswordCB."""

    success: bool
    result: OnReqAccountResetPasswordCBParsedMsgData
    msg_id: int = msgspec.client.onReqAccountResetPasswordCB.id
    text: str = ""


class OnReqAccountResetPasswordCBMsgParser(IMsgParser):
    """Парсер для Client::onReqAccountResetPasswordCB."""

    def parse(self, msg: Message) -> OnReqAccountResetPasswordCBMsgParserResult:
        """Распарсить сообщение Client::onReqAccountResetPasswordCB.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnReqAccountResetPasswordCBMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        code = values[0]
        return OnReqAccountResetPasswordCBMsgParserResult(
            success=True,
            result=OnReqAccountResetPasswordCBParsedMsgData(code),
        )


@dataclass
class OnReqAccountBindEmailCBParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onReqAccountBindEmailCB."""

    retCode: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name

    @property
    def ret_code(self) -> ServerError:
        """Возвращает код ошибки в виде enum ServerError.

        Returns:
            ServerError: Код ошибки

        """
        return ServerError(self.retCode)

    __add_to_dict__: ClassVar = ("ret_code",)


@dataclass(frozen=True)
class OnReqAccountBindEmailCBMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onReqAccountBindEmailCB."""

    success: bool
    result: OnReqAccountBindEmailCBParsedMsgData
    msg_id: int = msgspec.client.onReqAccountBindEmailCB.id
    text: str = ""


class OnReqAccountBindEmailCBMsgParser(IMsgParser):
    """Парсер для Client::onReqAccountBindEmailCB."""

    def parse(self, msg: Message) -> OnReqAccountBindEmailCBMsgParserResult:
        """Распарсить сообщение Client::onReqAccountBindEmailCB.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnReqAccountBindEmailCBMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        code = values[0]
        return OnReqAccountBindEmailCBMsgParserResult(
            success=True, result=OnReqAccountBindEmailCBParsedMsgData(code)
        )


@dataclass
class OnReqAccountNewPasswordCBParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onReqAccountNewPasswordCB."""

    retCode: KBEUInt16  # noqa: N815  # pylint: disable=invalid-name

    @property
    def ret_code(self) -> ServerError:
        """Возвращает код ошибки в виде enum ServerError.

        Returns:
            ServerError: Код ошибки

        """
        return ServerError(self.retCode)

    __add_to_dict__: ClassVar = ("ret_code",)


@dataclass(frozen=True)
class OnReqAccountNewPasswordCBMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onReqAccountNewPasswordCB."""

    success: bool
    result: OnReqAccountNewPasswordCBParsedMsgData
    msg_id: int = msgspec.client.onReqAccountNewPasswordCB.id
    text: str = ""


class OnReqAccountNewPasswordCBMsgParser(IMsgParser):
    """Парсер для Client::onReqAccountNewPasswordCB."""

    def parse(self, msg: Message) -> OnReqAccountNewPasswordCBMsgParserResult:
        """Распарсить сообщение Client::onReqAccountNewPasswordCB.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnReqAccountNewPasswordCBMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        code = values[0]
        return OnReqAccountNewPasswordCBMsgParserResult(
            success=True, result=OnReqAccountNewPasswordCBParsedMsgData(code)
        )


@dataclass
class OnRemoteMethodCallParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onRemoteMethodCall."""

    method_data: KBERowByteData


@dataclass(frozen=True)
class OnRemoteMethodCallMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onRemoteMethodCall."""

    success: bool
    result: OnRemoteMethodCallParsedMsgData
    msg_id: int = msgspec.client.onRemoteMethodCall.id
    text: str = ""


class OnRemoteMethodCallMsgParser(IMsgParser):
    """Парсер для Client::onRemoteMethodCall."""

    def parse(self, msg: Message) -> OnRemoteMethodCallMsgParserResult:
        """Распарсить сообщение Client::onRemoteMethodCall.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnRemoteMethodCallMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnRemoteMethodCallMsgParserResult(
            success=True, result=OnRemoteMethodCallParsedMsgData(data)
        )


@dataclass
class OnUpdateDataYprParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_ypr."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataYprMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_ypr."""

    success: bool
    result: OnUpdateDataYprParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_ypr.id
    text: str = ""


class OnUpdateDataYprMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_ypr."""

    def parse(self, msg: Message) -> OnUpdateDataYprMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_ypr.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataYprMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataYprMsgParserResult(
            success=True, result=OnUpdateDataYprParsedMsgData(data)
        )


@dataclass
class OnUpdateDataYpParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_yp."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataYpMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_yp."""

    success: bool
    result: OnUpdateDataYpParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_yp.id
    text: str = ""


class OnUpdateDataYpMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_yp."""

    def parse(self, msg: Message) -> OnUpdateDataYpMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_yp.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataYpMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataYpMsgParserResult(
            success=True, result=OnUpdateDataYpParsedMsgData(data)
        )


@dataclass
class OnUpdateDataYrParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_yr."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataYrMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_yr."""

    success: bool
    result: OnUpdateDataYrParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_yr.id
    text: str = ""


class OnUpdateDataYrMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_yr."""

    def parse(self, msg: Message) -> OnUpdateDataYrMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_yr.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataYrMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataYrMsgParserResult(
            success=True, result=OnUpdateDataYrParsedMsgData(data)
        )


@dataclass
class OnUpdateDataPrParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_pr."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataPrMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_pr."""

    success: bool
    result: OnUpdateDataPrParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_pr.id
    text: str = ""


class OnUpdateDataPrMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_pr."""

    def parse(self, msg: Message) -> OnUpdateDataPrMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_pr.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataPrMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataPrMsgParserResult(
            success=True, result=OnUpdateDataPrParsedMsgData(data)
        )


@dataclass
class OnUpdateDataYParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_y."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataYMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_y."""

    success: bool
    result: OnUpdateDataYParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_y.id
    text: str = ""


class OnUpdateDataYMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_y."""

    def parse(self, msg: Message) -> OnUpdateDataYMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_y.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataYMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataYMsgParserResult(
            success=True, result=OnUpdateDataYParsedMsgData(data)
        )


@dataclass
class OnUpdateDataPParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_p."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataPMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_p."""

    success: bool
    result: OnUpdateDataPParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_p.id
    text: str = ""


class OnUpdateDataPMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_p."""

    def parse(self, msg: Message) -> OnUpdateDataPMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_p.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataPMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataPMsgParserResult(
            success=True, result=OnUpdateDataPParsedMsgData(data)
        )


@dataclass
class OnUpdateDataRParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_r."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataRMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_r."""

    success: bool
    result: OnUpdateDataRParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_r.id
    text: str = ""


class OnUpdateDataRMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_r."""

    def parse(self, msg: Message) -> OnUpdateDataRMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_r.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataRMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataRMsgParserResult(
            success=True, result=OnUpdateDataRParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz."""

    success: bool
    result: OnUpdateDataXzParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz.id
    text: str = ""


class OnUpdateDataXzMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz."""

    def parse(self, msg: Message) -> OnUpdateDataXzMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzMsgParserResult(
            success=True, result=OnUpdateDataXzParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzYprParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_ypr."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzYprMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_ypr."""

    success: bool
    result: OnUpdateDataXzYprParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_ypr.id
    text: str = ""


class OnUpdateDataXzYprMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_ypr."""

    def parse(self, msg: Message) -> OnUpdateDataXzYprMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_ypr.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzYprMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzYprMsgParserResult(
            success=True, result=OnUpdateDataXzYprParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzYpParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_yp."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzYpMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_yp."""

    success: bool
    result: OnUpdateDataXzYpParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_yp.id
    text: str = ""


class OnUpdateDataXzYpMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_yp."""

    def parse(self, msg: Message) -> OnUpdateDataXzYpMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_yp.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzYpMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzYpMsgParserResult(
            success=True, result=OnUpdateDataXzYpParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzYrParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_yr."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzYrMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_yr."""

    success: bool
    result: OnUpdateDataXzYrParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_yr.id
    text: str = ""


class OnUpdateDataXzYrMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_yr."""

    def parse(self, msg: Message) -> OnUpdateDataXzYrMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_yr.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzYrMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzYrMsgParserResult(
            success=True, result=OnUpdateDataXzYrParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzPrParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_pr."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzPrMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_pr."""

    success: bool
    result: OnUpdateDataXzPrParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_pr.id
    text: str = ""


class OnUpdateDataXzPrMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_pr."""

    def parse(self, msg: Message) -> OnUpdateDataXzPrMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_pr.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzPrMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzPrMsgParserResult(
            success=True, result=OnUpdateDataXzPrParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzYParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_y."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzYMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_y."""

    success: bool
    result: OnUpdateDataXzYParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_y.id
    text: str = ""


class OnUpdateDataXzYMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_y."""

    def parse(self, msg: Message) -> OnUpdateDataXzYMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_y.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzYMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzYMsgParserResult(
            success=True, result=OnUpdateDataXzYParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzPParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_p."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzPMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_p."""

    success: bool
    result: OnUpdateDataXzPParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_p.id
    text: str = ""


class OnUpdateDataXzPMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_p."""

    def parse(self, msg: Message) -> OnUpdateDataXzPMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_p.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzPMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzPMsgParserResult(
            success=True, result=OnUpdateDataXzPParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzRParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_r."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzRMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_r."""

    success: bool
    result: OnUpdateDataXzRParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_r.id
    text: str = ""


class OnUpdateDataXzRMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_r."""

    def parse(self, msg: Message) -> OnUpdateDataXzRMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_r.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzRMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzRMsgParserResult(
            success=True, result=OnUpdateDataXzRParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz."""

    success: bool
    result: OnUpdateDataXyzParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz.id
    text: str = ""


class OnUpdateDataXyzMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz."""

    def parse(self, msg: Message) -> OnUpdateDataXyzMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzMsgParserResult(
            success=True, result=OnUpdateDataXyzParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzYprParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_ypr."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzYprMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_ypr."""

    success: bool
    result: OnUpdateDataXyzYprParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_ypr.id
    text: str = ""


class OnUpdateDataXyzYprMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_ypr."""

    def parse(self, msg: Message) -> OnUpdateDataXyzYprMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_ypr.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzYprMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzYprMsgParserResult(
            success=True, result=OnUpdateDataXyzYprParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzYpParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_yp."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzYpMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_yp."""

    success: bool
    result: OnUpdateDataXyzYpParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_yp.id
    text: str = ""


class OnUpdateDataXyzYpMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_yp."""

    def parse(self, msg: Message) -> OnUpdateDataXyzYpMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_yp.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzYpMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzYpMsgParserResult(
            success=True, result=OnUpdateDataXyzYpParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzYrParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_yr."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzYrMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_yr."""

    success: bool
    result: OnUpdateDataXyzYrParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_yr.id
    text: str = ""


class OnUpdateDataXyzYrMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_yr."""

    def parse(self, msg: Message) -> OnUpdateDataXyzYrMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_yr.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzYrMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzYrMsgParserResult(
            success=True, result=OnUpdateDataXyzYrParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzPrParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_pr."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzPrMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_pr."""

    success: bool
    result: OnUpdateDataXyzPrParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_pr.id
    text: str = ""


class OnUpdateDataXyzPrMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_pr."""

    def parse(self, msg: Message) -> OnUpdateDataXyzPrMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_pr.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzPrMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzPrMsgParserResult(
            success=True, result=OnUpdateDataXyzPrParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzYParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_y."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzYMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_y."""

    success: bool
    result: OnUpdateDataXyzYParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_y.id
    text: str = ""


class OnUpdateDataXyzYMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_y."""

    def parse(self, msg: Message) -> OnUpdateDataXyzYMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_y.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzYMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzYMsgParserResult(
            success=True, result=OnUpdateDataXyzYParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzPParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_p."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzPMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_p."""

    success: bool
    result: OnUpdateDataXyzPParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_p.id
    text: str = ""


class OnUpdateDataXyzPMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_p."""

    def parse(self, msg: Message) -> OnUpdateDataXyzPMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_p.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzPMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzPMsgParserResult(
            success=True, result=OnUpdateDataXyzPParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzRParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_r."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzRMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_r."""

    success: bool
    result: OnUpdateDataXyzRParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_r.id
    text: str = ""


class OnUpdateDataXyzRMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_r."""

    def parse(self, msg: Message) -> OnUpdateDataXyzRMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_r.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzRMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzRMsgParserResult(
            success=True, result=OnUpdateDataXyzRParsedMsgData(data)
        )


@dataclass
class OnUpdateDataYprOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_ypr_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataYprOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_ypr_optimized."""

    success: bool
    result: OnUpdateDataYprOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_ypr_optimized.id
    text: str = ""


class OnUpdateDataYprOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_ypr_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataYprOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_ypr_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataYprOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataYprOptimizedMsgParserResult(
            success=True, result=OnUpdateDataYprOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataYpOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_yp_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataYpOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_yp_optimized."""

    success: bool
    result: OnUpdateDataYpOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_yp_optimized.id
    text: str = ""


class OnUpdateDataYpOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_yp_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataYpOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_yp_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataYpOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataYpOptimizedMsgParserResult(
            success=True, result=OnUpdateDataYpOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataYrOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_yr_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataYrOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_yr_optimized."""

    success: bool
    result: OnUpdateDataYrOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_yr_optimized.id
    text: str = ""


class OnUpdateDataYrOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_yr_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataYrOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_yr_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataYrOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataYrOptimizedMsgParserResult(
            success=True, result=OnUpdateDataYrOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataPrOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_pr_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataPrOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_pr_optimized."""

    success: bool
    result: OnUpdateDataPrOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_pr_optimized.id
    text: str = ""


class OnUpdateDataPrOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_pr_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataPrOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_pr_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataPrOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataPrOptimizedMsgParserResult(
            success=True, result=OnUpdateDataPrOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataYOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_y_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataYOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_y_optimized."""

    success: bool
    result: OnUpdateDataYOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_y_optimized.id
    text: str = ""


class OnUpdateDataYOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_y_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataYOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_y_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataYOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataYOptimizedMsgParserResult(
            success=True, result=OnUpdateDataYOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataPOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_p_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataPOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_p_optimized."""

    success: bool
    result: OnUpdateDataPOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_p_optimized.id
    text: str = ""


class OnUpdateDataPOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_p_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataPOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_p_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataPOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataPOptimizedMsgParserResult(
            success=True, result=OnUpdateDataPOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataROptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_r_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataROptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_r_optimized."""

    success: bool
    result: OnUpdateDataROptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_r_optimized.id
    text: str = ""


class OnUpdateDataROptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_r_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataROptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_r_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataROptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataROptimizedMsgParserResult(
            success=True, result=OnUpdateDataROptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_optimized."""

    success: bool
    result: OnUpdateDataXzOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_optimized.id
    text: str = ""


class OnUpdateDataXzOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXzOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzOptimizedMsgParserResult(
            success=True, result=OnUpdateDataXzOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzYprOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_ypr_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzYprOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_ypr_optimized."""

    success: bool
    result: OnUpdateDataXzYprOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_ypr_optimized.id
    text: str = ""


class OnUpdateDataXzYprOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_ypr_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXzYprOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_ypr_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzYprOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzYprOptimizedMsgParserResult(
            success=True, result=OnUpdateDataXzYprOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzYpOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_yp_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzYpOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_yp_optimized."""

    success: bool
    result: OnUpdateDataXzYpOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_yp_optimized.id
    text: str = ""


class OnUpdateDataXzYpOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_yp_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXzYpOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_yp_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzYpOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzYpOptimizedMsgParserResult(
            success=True, result=OnUpdateDataXzYpOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzYrOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_yr_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzYrOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_yr_optimized."""

    success: bool
    result: OnUpdateDataXzYrOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_yr_optimized.id
    text: str = ""


class OnUpdateDataXzYrOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_yr_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXzYrOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_yr_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzYrOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzYrOptimizedMsgParserResult(
            success=True, result=OnUpdateDataXzYrOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzPrOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_pr_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzPrOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_pr_optimized."""

    success: bool
    result: OnUpdateDataXzPrOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_pr_optimized.id
    text: str = ""


class OnUpdateDataXzPrOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_pr_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXzPrOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_pr_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzPrOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzPrOptimizedMsgParserResult(
            success=True, result=OnUpdateDataXzPrOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzYOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_y_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzYOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_y_optimized."""

    success: bool
    result: OnUpdateDataXzYOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_y_optimized.id
    text: str = ""


class OnUpdateDataXzYOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_y_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXzYOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_y_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzYOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzYOptimizedMsgParserResult(
            success=True, result=OnUpdateDataXzYOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzPOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_p_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzPOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_p_optimized."""

    success: bool
    result: OnUpdateDataXzPOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_p_optimized.id
    text: str = ""


class OnUpdateDataXzPOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_p_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXzPOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_p_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzPOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzPOptimizedMsgParserResult(
            success=True, result=OnUpdateDataXzPOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXzROptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xz_r_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXzROptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xz_r_optimized."""

    success: bool
    result: OnUpdateDataXzROptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xz_r_optimized.id
    text: str = ""


class OnUpdateDataXzROptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xz_r_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXzROptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xz_r_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXzROptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXzROptimizedMsgParserResult(
            success=True, result=OnUpdateDataXzROptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_optimized."""

    success: bool
    result: OnUpdateDataXyzOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_optimized.id
    text: str = ""


class OnUpdateDataXyzOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXyzOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzOptimizedMsgParserResult(
            success=True, result=OnUpdateDataXyzOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzYprOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_ypr_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzYprOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_ypr_optimized."""

    success: bool
    result: OnUpdateDataXyzYprOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_ypr_optimized.id
    text: str = ""


class OnUpdateDataXyzYprOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_ypr_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXyzYprOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_ypr_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzYprOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzYprOptimizedMsgParserResult(
            success=True, result=OnUpdateDataXyzYprOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzYpOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_yp_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzYpOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_yp_optimized."""

    success: bool
    result: OnUpdateDataXyzYpOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_yp_optimized.id
    text: str = ""


class OnUpdateDataXyzYpOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_yp_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXyzYpOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_yp_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzYpOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzYpOptimizedMsgParserResult(
            success=True, result=OnUpdateDataXyzYpOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzYrOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_yr_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzYrOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_yr_optimized."""

    success: bool
    result: OnUpdateDataXyzYrOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_yr_optimized.id
    text: str = ""


class OnUpdateDataXyzYrOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_yr_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXyzYrOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_yr_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzYrOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzYrOptimizedMsgParserResult(
            success=True, result=OnUpdateDataXyzYrOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzPrOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_pr_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzPrOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_pr_optimized."""

    success: bool
    result: OnUpdateDataXyzPrOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_pr_optimized.id
    text: str = ""


class OnUpdateDataXyzPrOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_pr_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXyzPrOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_pr_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzPrOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzPrOptimizedMsgParserResult(
            success=True, result=OnUpdateDataXyzPrOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzYOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_y_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzYOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_y_optimized."""

    success: bool
    result: OnUpdateDataXyzYOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_y_optimized.id
    text: str = ""


class OnUpdateDataXyzYOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_y_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXyzYOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_y_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzYOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzYOptimizedMsgParserResult(
            success=True, result=OnUpdateDataXyzYOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzPOptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_p_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzPOptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_p_optimized."""

    success: bool
    result: OnUpdateDataXyzPOptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_p_optimized.id
    text: str = ""


class OnUpdateDataXyzPOptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_p_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXyzPOptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_p_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzPOptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzPOptimizedMsgParserResult(
            success=True, result=OnUpdateDataXyzPOptimizedParsedMsgData(data)
        )


@dataclass
class OnUpdateDataXyzROptimizedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onUpdateData_xyz_r_optimized."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnUpdateDataXyzROptimizedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onUpdateData_xyz_r_optimized."""

    success: bool
    result: OnUpdateDataXyzROptimizedParsedMsgData | None
    msg_id: int = msgspec.client.onUpdateData_xyz_r_optimized.id
    text: str = ""


class OnUpdateDataXyzROptimizedMsgParser(IMsgParser):
    """Парсер для Client::onUpdateData_xyz_r_optimized."""

    def parse(self, msg: Message) -> OnUpdateDataXyzROptimizedMsgParserResult:
        """Распарсить сообщение Client::onUpdateData_xyz_r_optimized.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnUpdateDataXyzROptimizedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnUpdateDataXyzROptimizedMsgParserResult(
            success=True, result=OnUpdateDataXyzROptimizedParsedMsgData(data)
        )


@dataclass
class OnImportClientSDKParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onImportClientSDK."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnImportClientSDKMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onImportClientSDK."""

    success: bool
    result: OnImportClientSDKParsedMsgData | None
    msg_id: int = msgspec.client.onImportClientSDK.id
    text: str = ""


class OnImportClientSDKMsgParser(IMsgParser):
    """Парсер для Client::onImportClientSDK."""

    def parse(self, msg: Message) -> OnImportClientSDKMsgParserResult:
        """Распарсить сообщение Client::onImportClientSDK.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnImportClientSDKMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnImportClientSDKMsgParserResult(
            success=True, result=OnImportClientSDKParsedMsgData(data)
        )


@dataclass
class InitSpaceDataParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::initSpaceData."""

    data: KBERowByteData


@dataclass(frozen=True)
class InitSpaceDataMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::initSpaceData."""

    success: bool
    result: InitSpaceDataParsedMsgData | None
    msg_id: int = msgspec.client.initSpaceData.id
    text: str = ""


class InitSpaceDataMsgParser(IMsgParser):
    """Парсер для Client::initSpaceData."""

    def parse(self, msg: Message) -> InitSpaceDataMsgParserResult:
        """Распарсить сообщение Client::initSpaceData.

        Args:
            msg: Сообщение для парсинга

        Returns:
            InitSpaceDataMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return InitSpaceDataMsgParserResult(
            success=True, result=InitSpaceDataParsedMsgData(data)
        )


@dataclass
class OnReloginBaseappSuccessfullyParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onReloginBaseappSuccessfully."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnReloginBaseappSuccessfullyMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onReloginBaseappSuccessfully."""

    success: bool
    result: OnReloginBaseappSuccessfullyParsedMsgData | None
    msg_id: int = msgspec.client.onReloginBaseappSuccessfully.id
    text: str = ""


class OnReloginBaseappSuccessfullyMsgParser(IMsgParser):
    """Парсер для Client::onReloginBaseappSuccessfully."""

    def parse(
        self, msg: Message
    ) -> OnReloginBaseappSuccessfullyMsgParserResult:
        """Распарсить сообщение Client::onReloginBaseappSuccessfully.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnReloginBaseappSuccessfullyMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnReloginBaseappSuccessfullyMsgParserResult(
            success=True, result=OnReloginBaseappSuccessfullyParsedMsgData(data)
        )


@dataclass
class OnCreateAccountResultParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onCreateAccountResult."""

    retCode: KBEServerErrorCode  # noqa: N815  # pylint: disable=invalid-name
    data: KBERowByteData

    @property
    def ret_code(self) -> ServerError:
        """Возвращает код ошибки в виде enum ServerError.

        Returns:
            ServerError: Код ошибки

        """
        return ServerError(self.retCode)

    __add_to_dict__: ClassVar = ("ret_code",)


@dataclass(frozen=True)
class OnCreateAccountResultMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onCreateAccountResult."""

    success: bool
    result: OnCreateAccountResultParsedMsgData | None
    msg_id: int = msgspec.client.onCreateAccountResult.id
    text: str = ""


class OnCreateAccountResultMsgParser(IMsgParser):
    """Парсер для Client::onCreateAccountResult."""

    def parse(self, msg: Message) -> OnCreateAccountResultMsgParserResult:
        """Распарсить сообщение Client::onCreateAccountResult.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnCreateAccountResultMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        return OnCreateAccountResultMsgParserResult(
            success=True, result=OnCreateAccountResultParsedMsgData(*values)
        )


@dataclass
class OnEntityEnterWorldParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onEntityEnterWorld."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnEntityEnterWorldMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onEntityEnterWorld."""

    success: bool
    result: OnEntityEnterWorldParsedMsgData | None
    msg_id: int = msgspec.client.onEntityEnterWorld.id
    text: str = ""


class OnEntityEnterWorldMsgParser(IMsgParser):
    """Парсер для Client::onEntityEnterWorld."""

    def parse(self, msg: Message) -> OnEntityEnterWorldMsgParserResult:
        """Распарсить сообщение Client::onEntityEnterWorld.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnEntityEnterWorldMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnEntityEnterWorldMsgParserResult(
            success=True, result=OnEntityEnterWorldParsedMsgData(data)
        )


@dataclass
class OnEntityLeaveSpaceParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onEntityLeaveSpace."""

    entity_id: int


@dataclass(frozen=True)
class OnEntityLeaveSpaceMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onEntityLeaveSpace."""

    success: bool
    result: OnEntityLeaveSpaceParsedMsgData | None
    msg_id: int = msgspec.client.onEntityLeaveSpace.id
    text: str = ""


class OnEntityLeaveSpaceMsgParser(IMsgParser):
    """Парсер для Client::onEntityLeaveSpace."""

    def parse(self, msg: Message) -> OnEntityLeaveSpaceMsgParserResult:
        """Распарсить сообщение Client::onEntityLeaveSpace.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnEntityLeaveSpaceMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        entity_id = values[0]
        return OnEntityLeaveSpaceMsgParserResult(
            success=True, result=OnEntityLeaveSpaceParsedMsgData(entity_id)
        )


@dataclass
class OnEntityEnterSpaceParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onEntityEnterSpace."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnEntityEnterSpaceMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onEntityEnterSpace."""

    success: bool
    result: OnEntityEnterSpaceParsedMsgData | None
    msg_id: int = msgspec.client.onEntityEnterSpace.id
    text: str = ""


class OnEntityEnterSpaceMsgParser(IMsgParser):
    """Парсер для Client::onEntityEnterSpace."""

    def parse(self, msg: Message) -> OnEntityEnterSpaceMsgParserResult:
        """Распарсить сообщение Client::onEntityEnterSpace.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnEntityEnterSpaceMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnEntityEnterSpaceMsgParserResult(
            success=True, result=OnEntityEnterSpaceParsedMsgData(data)
        )


@dataclass
class OnStreamDataStartedParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onStreamDataStarted."""

    stream_id: int
    resource_size: int
    resource_name: KBEString
    stream_type: int


@dataclass(frozen=True)
class OnStreamDataStartedMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onStreamDataStarted."""

    success: bool
    result: OnStreamDataStartedParsedMsgData | None
    msg_id: int = msgspec.client.onStreamDataStarted.id
    text: str = ""


class OnStreamDataStartedMsgParser(IMsgParser):
    """Парсер для Client::onStreamDataStarted."""

    def parse(self, msg: Message) -> OnStreamDataStartedMsgParserResult:
        """Распарсить сообщение Client::onStreamDataStarted.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnStreamDataStartedMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        stream_id, resource_size, resource_name, stream_type = values
        return OnStreamDataStartedMsgParserResult(
            success=True,
            result=OnStreamDataStartedParsedMsgData(
                stream_id, resource_size, resource_name, stream_type
            ),
        )


@dataclass
class OnStreamDataRecvParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onStreamDataRecv."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnStreamDataRecvMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onStreamDataRecv."""

    success: bool
    result: OnStreamDataRecvParsedMsgData | None
    msg_id: int = msgspec.client.onStreamDataRecv.id
    text: str = ""


class OnStreamDataRecvMsgParser(IMsgParser):
    """Парсер для Client::onStreamDataRecv."""

    def parse(self, msg: Message) -> OnStreamDataRecvMsgParserResult:
        """Распарсить сообщение Client::onStreamDataRecv.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnStreamDataRecvMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnStreamDataRecvMsgParserResult(
            success=True, result=OnStreamDataRecvParsedMsgData(data)
        )


@dataclass
class OnImportClientEntityDefParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onImportClientEntityDef."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnImportClientEntityDefMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onImportClientEntityDef."""

    success: bool
    result: OnImportClientEntityDefParsedMsgData | None
    msg_id: int = msgspec.client.onImportClientEntityDef.id
    text: str = ""


class OnImportClientEntityDefMsgParser(IMsgParser):
    """Парсер для Client::onImportClientEntityDef."""

    def parse(self, msg: Message) -> OnImportClientEntityDefMsgParserResult:
        """Распарсить сообщение Client::onImportClientEntityDef.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnImportClientEntityDefMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnImportClientEntityDefMsgParserResult(
            success=True, result=OnImportClientEntityDefParsedMsgData(data)
        )


@dataclass
class OnImportServerErrorsDescrParsedMsgData(ParsedMsgData):
    """Данные распарсенного сообщения Client::onImportServerErrorsDescr."""

    data: KBERowByteData


@dataclass(frozen=True)
class OnImportServerErrorsDescrMsgParserResult(MsgParserResult):
    """Результат обработки сообщения Client::onImportServerErrorsDescr."""

    success: bool
    result: OnImportServerErrorsDescrParsedMsgData | None
    msg_id: int = msgspec.client.onImportServerErrorsDescr.id
    text: str = ""


class OnImportServerErrorsDescrMsgParser(IMsgParser):
    """Парсер для Client::onImportServerErrorsDescr."""

    def parse(self, msg: Message) -> OnImportServerErrorsDescrMsgParserResult:
        """Распарсить сообщение Client::onImportServerErrorsDescr.

        Args:
            msg: Сообщение для парсинга

        Returns:
            OnImportServerErrorsDescrMsgParserResult: Результат парсинга

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = KBERowByteData(values[0])
        return OnImportServerErrorsDescrMsgParserResult(
            success=True, result=OnImportServerErrorsDescrParsedMsgData(data)
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
