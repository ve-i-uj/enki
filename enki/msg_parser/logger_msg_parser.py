"""Обработчик сообщений от компонента Logger."""

import logging
from dataclasses import dataclass
from typing import Any, ClassVar

from enki import msgspec
from enki.kbeenum import (
    COMPONENT_STATE_BY_SHUTDOWN_STATE,
    ComponentState,
    ComponentType,
    ShutdownState,
)
from enki.kbetype.decoders.custom_decoders import (
    KBEComponentId,
    KBEComponentOrderId,
    KBEComponentType,
    KBEGameTime,
    KBEShutdownState,
    KBEUid,
)
from enki.kbetype.pytypes.basic_data_types import KBEBlob, KBEInt64, KBEUInt32
from enki.misc import devonly
from enki.msg.message import Message
from enki.msg_parser.common import OnRegisterNewAppParsedMsgData
from enki.msg_parser.imsg_parser import (
    IMsgParser,
    MsgParserResult,
    ParsedMsgData,
)

logger = logging.getLogger(__name__)


@dataclass
class OnAppActiveTickParsedMsgData(ParsedMsgData):
    """Parsed message Logger::onAppActiveTick."""

    componentType: KBEComponentType  # pylint: disable=invalid-name
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name

    @property
    def component_type(self) -> ComponentType:
        """Enum reflecting componentType value.

        Returns:
            ComponentType: component type

        """
        return ComponentType(self.componentType)

    __add_to_dict__: ClassVar = ("component_type",)


@dataclass(frozen=True)
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Result of Logger::onAppActiveTick message parser."""

    success: bool
    result: OnAppActiveTickParsedMsgData
    msg_id: int = msgspec.logger.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    """Parser for Logger::onAppActiveTick."""

    def parse(self, msg: Message) -> OnAppActiveTickMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedMsgData(*values)
        return OnAppActiveTickMsgParserResult(success=True, result=pd)


@dataclass(frozen=True)
class OnRegisterNewAppMsgParserResult(MsgParserResult):
    """Result of Logger::onRegisterNewApp message parser."""

    success: bool
    result: OnRegisterNewAppParsedMsgData
    msg_id: int = msgspec.logger.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    """Parser for Logger::onRegisterNewApp."""

    def parse(self, msg: Message) -> OnRegisterNewAppMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedMsgData(*values)
        return OnRegisterNewAppMsgParserResult(True, pd)


@dataclass
class WriteLogParsedMsgData(ParsedMsgData):
    """Parsed message Logger::writeLog."""

    uid: KBEUid
    logtype: KBEUInt32
    componentType: KBEComponentType  # pylint: disable=invalid-name
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    globalorderID: KBEComponentOrderId  # pylint: disable=invalid-name
    grouporderID: KBEComponentOrderId  # pylint: disable=invalid-name
    time: KBEInt64
    kbetime: KBEGameTime
    log_size_and_text: KBEBlob

    @property
    def component_type(self) -> ComponentType:
        """Enum reflecting componentType value.

        Returns:
            ComponentType: component type

        """
        return ComponentType(self.componentType)

    __add_to_dict__: ClassVar = ("component_type",)


@dataclass(frozen=True)
class WriteLogMsgParserResult(MsgParserResult):
    """Result of Logger::writeLog message parser."""

    success: bool
    result: WriteLogParsedMsgData
    msg_id: int = msgspec.logger.writeLog.id
    text: str = ""


class WriteLogMsgParser(IMsgParser):
    """Parser for Logger::writeLog."""

    def parse(self, msg: Message) -> WriteLogMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = WriteLogParsedMsgData(*values)
        return WriteLogMsgParserResult(success=True, result=pd)


@dataclass
class RegisterLogWatcherParsedMsgData(ParsedMsgData):
    """Parsed message Logger::registerLogWatcher."""

    uid: KBEUid
    logtypes_filter: KBEUInt32
    globalOrder: KBEComponentOrderId  # pylint: disable=invalid-name
    groupOrder: KBEComponentOrderId  # pylint: disable=invalid-name
    date: str
    keyStr: str  # pylint: disable=invalid-name
    component_type_filter: bytes  # UINT8_ARRAY
    isfind: bool
    first: bool


@dataclass(frozen=True)
class RegisterLogWatcherMsgParserResult(MsgParserResult):
    """Result of Logger::registerLogWatcher message parser."""

    success: bool
    result: RegisterLogWatcherParsedMsgData
    msg_id: int = msgspec.logger.registerLogWatcher.id
    text: str = ""


class RegisterLogWatcherMsgParser(IMsgParser):
    """Parser for Logger::registerLogWatcher."""

    def parse(self, msg: Message) -> RegisterLogWatcherMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = RegisterLogWatcherParsedMsgData(*values)
        return RegisterLogWatcherMsgParserResult(success=True, result=pd)


@dataclass
class DeregisterLogWatcherParsedMsgData(ParsedMsgData):
    """Parsed message Logger::deregisterLogWatcher (empty)."""


@dataclass(frozen=True)
class DeregisterLogWatcherMsgParserResult(MsgParserResult):
    """Result of Logger::deregisterLogWatcher message parser."""

    success: bool
    result: DeregisterLogWatcherParsedMsgData
    msg_id: int = msgspec.logger.deregisterLogWatcher.id
    text: str = ""


class DeregisterLogWatcherMsgParser(IMsgParser):
    """Parser for Logger::deregisterLogWatcher."""

    def parse(self, msg: Message) -> DeregisterLogWatcherMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        # deregisterLogWatcher has no arguments
        pd = DeregisterLogWatcherParsedMsgData()
        return DeregisterLogWatcherMsgParserResult(success=True, result=pd)


@dataclass
class UpdateLogWatcherSettingParsedMsgData(ParsedMsgData):
    """Parsed message Logger::updateLogWatcherSetting."""

    uid: KBEUid
    logtypes_filter: KBEUInt32
    globalOrder: KBEComponentOrderId  # pylint: disable=invalid-name
    groupOrder: KBEComponentOrderId  # pylint: disable=invalid-name
    date: str
    keyStr: str  # pylint: disable=invalid-name
    component_type_filter: bytes  # UINT8_ARRAY


@dataclass(frozen=True)
class UpdateLogWatcherSettingMsgParserResult(MsgParserResult):
    """Result of Logger::updateLogWatcherSetting message parser."""

    success: bool
    result: UpdateLogWatcherSettingParsedMsgData
    msg_id: int = msgspec.logger.updateLogWatcherSetting.id
    text: str = ""


class UpdateLogWatcherSettingMsgParser(IMsgParser):
    """Parser for Logger::updateLogWatcherSetting."""

    def parse(self, msg: Message) -> UpdateLogWatcherSettingMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = UpdateLogWatcherSettingParsedMsgData(*values)
        return UpdateLogWatcherSettingMsgParserResult(success=True, result=pd)


@dataclass
class QueryWatcherParsedMsgData(ParsedMsgData):
    """Parsed message Logger::queryWatcher."""

    path: str


@dataclass(frozen=True)
class QueryWatcherMsgParserResult(MsgParserResult):
    """Result of Logger::queryWatcher message parser."""

    success: bool
    result: QueryWatcherParsedMsgData
    msg_id: int = msgspec.logger.queryWatcher.id
    text: str = ""


class QueryWatcherMsgParser(IMsgParser):
    """Parser for Logger::queryWatcher."""

    def parse(self, msg: Message) -> QueryWatcherMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = QueryWatcherParsedMsgData(*values)
        return QueryWatcherMsgParserResult(success=True, result=pd)


@dataclass
class StartProfileParsedMsgData(ParsedMsgData):
    """Parsed message Logger::startProfile."""

    profileName: str  # pylint: disable=invalid-name
    profileType: int
    timelen: KBEUInt32


@dataclass(frozen=True)
class StartProfileMsgParserResult(MsgParserResult):
    """Result of Logger::startProfile message parser."""

    success: bool
    result: StartProfileParsedMsgData
    msg_id: int = msgspec.logger.startProfile.id
    text: str = ""


class StartProfileMsgParser(IMsgParser):
    """Parser for Logger::startProfile."""

    def parse(self, msg: Message) -> StartProfileMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = StartProfileParsedMsgData(*values)
        return StartProfileMsgParserResult(success=True, result=pd)


@dataclass
class ReqKillServerParsedMsgData(ParsedMsgData):
    """Parsed message Logger::reqKillServer."""

    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    componentType: KBEComponentType  # pylint: disable=invalid-name
    username: str
    uid: KBEUid
    reason: str

    @property
    def component_type(self) -> ComponentType:
        """Enum reflecting componentType value.

        Returns:
            ComponentType: component type

        """
        return ComponentType(self.componentType)

    __add_to_dict__: ClassVar = ("component_type",)


@dataclass(frozen=True)
class ReqKillServerMsgParserResult(MsgParserResult):
    """Result of Logger::reqKillServer message parser."""

    success: bool
    result: ReqKillServerParsedMsgData
    msg_id: int = msgspec.logger.reqKillServer.id
    text: str = ""


class ReqKillServerMsgParser(IMsgParser):
    """Parser for Logger::reqKillServer."""

    def parse(self, msg: Message) -> ReqKillServerMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqKillServerParsedMsgData(*values)
        return ReqKillServerMsgParserResult(success=True, result=pd)


@dataclass
class ReqCloseServerParsedMsgData(ParsedMsgData):
    """Parsed message Logger::reqCloseServer (empty)."""


@dataclass(frozen=True)
class ReqCloseServerMsgParserResult(MsgParserResult):
    """Result of Logger::reqCloseServer message parser."""

    success: bool
    result: ReqCloseServerParsedMsgData
    msg_id: int = msgspec.logger.reqCloseServer.id
    text: str = ""


class ReqCloseServerMsgParser(IMsgParser):
    """Parser for Logger::reqCloseServer."""

    def parse(self, msg: Message) -> ReqCloseServerMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        # reqCloseServer has no arguments
        pd = ReqCloseServerParsedMsgData()
        return ReqCloseServerMsgParserResult(success=True, result=pd)


@dataclass
class LookAppParsedMsgData(ParsedMsgData):
    """Parsed message Logger::lookApp (empty)."""


@dataclass(frozen=True)
class LookAppMsgParserResult(MsgParserResult):
    """Result of Logger::lookApp message parser."""

    success: bool
    result: LookAppParsedMsgData
    msg_id: int = msgspec.logger.lookApp.id
    text: str = ""


class LookAppMsgParser(IMsgParser):
    """Parser for Logger::lookApp."""

    def parse(self, msg: Message) -> LookAppMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        # lookApp has no arguments
        pd = LookAppParsedMsgData()
        return LookAppMsgParserResult(success=True, result=pd)


@dataclass
class QueryLoadParsedMsgData(ParsedMsgData):
    """Parsed message Logger::queryLoad (empty)."""


@dataclass(frozen=True)
class QueryLoadMsgParserResult(MsgParserResult):
    """Result of Logger::queryLoad message parser."""

    success: bool
    result: QueryLoadParsedMsgData
    msg_id: int = msgspec.logger.queryLoad.id
    text: str = ""


class QueryLoadMsgParser(IMsgParser):
    """Parser for Logger::queryLoad."""

    def parse(self, msg: Message) -> QueryLoadMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        # queryLoad has no arguments
        pd = QueryLoadParsedMsgData()
        return QueryLoadMsgParserResult(success=True, result=pd)


@dataclass
class OnLookAppParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Interfaces::onLookApp."""

    componentType: KBEComponentType  # noqa: N815
    componentId: KBEComponentId  # noqa: N815
    shutdownState: KBEShutdownState  # noqa: N815

    @property
    def component_type(self) -> ComponentType:
        """Возвращает тип компонента в виде enum ComponentType.

        Returns:
            ComponentType: Тип текущего компонента

        """
        return ComponentType(self.componentType)

    @property
    def component_state(self) -> ComponentState:
        """Возвращает состояние компонента.

        Returns:
            ComponentType: Тип текущего компонента

        """
        return COMPONENT_STATE_BY_SHUTDOWN_STATE[
            ShutdownState(self.shutdownState)
        ]

    __add_to_dict__: ClassVar = ("component_type", "component_state")


@dataclass(frozen=True)
class OnLookAppParserMsgParserResult(MsgParserResult):
    """Парсер для Interfaces::onLookApp."""

    success: bool
    result: OnLookAppParsedMsgData
    msg_id: int = msgspec.interfaces.onLookApp.id
    text: str = ""


class OnLookAppMsgParser(IMsgParser):
    """Парсер для Interfaces::onLookApp."""

    def parse(self, msg: Message) -> OnLookAppParserMsgParserResult:
        """Распарсить сообщение Interfaces::onLookApp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnLookAppParserMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnLookAppParsedMsgData(*values)
        return OnLookAppParserMsgParserResult(success=True, result=pd)
