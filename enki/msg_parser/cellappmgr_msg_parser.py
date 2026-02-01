"""Парсер сообщений от компонента CellappMgr."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from enki import msgspec
from enki.kbeenum import (
    COMPONENT_STATE_BY_SHUTDOWN_STATE,
    ComponentState,
    ComponentType,
    ShutdownState,
)
from enki.misc import devonly

from .common import (
    CreateCellEntityInNewSpaceFromBaseappParsedMsgData,
    CreateCellEntityInNewSpaceFromBaseappParser,
    LookAppParsedMsgData,
    OnAppActiveTickParsedMsgData,
    OnRegisterNewAppParsedMsgData,
)
from .imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

if TYPE_CHECKING:
    from enki.kbetype.decoders.custom_decoders import (
        KBEComponentId,
        KBEComponentOrderId,
        KBEComponentType,
        KBEEntityId,
        KBEShutdownState,
        KBESpaceId,
    )
    from enki.kbetype.pytypes.basic_data_types import (
        KBEInt8,
        KBEString,
        KBEUInt32,
    )
    from enki.msg.message import Message

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OnAppActiveTickMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::onAppActiveTick."""

    success: bool
    result: OnAppActiveTickParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.onAppActiveTick.id
    text: str = ""


class OnAppActiveTickMsgParser(IMsgParser):
    """Парсер для Cellappmgr::onAppActiveTick."""

    def parse(self, msg: Message) -> OnAppActiveTickMsgParserResult:
        """Handle a message."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnAppActiveTickParsedMsgData(*values)
        return OnAppActiveTickMsgParserResult(True, pd)


@dataclass(frozen=True)
class OnRegisterNewAppMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::onRegisterNewApp."""

    success: bool
    result: OnRegisterNewAppParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.onRegisterNewApp.id
    text: str = ""


class OnRegisterNewAppMsgParser(IMsgParser):
    """Парсер для Cellappmgr::onRegisterNewApp."""

    def parse(self, msg: Message) -> OnRegisterNewAppMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnRegisterNewAppParsedMsgData(*values)
        return OnRegisterNewAppMsgParserResult(True, pd)


@dataclass(frozen=True)
class LookAppMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::lookApp."""

    success: bool
    result: LookAppParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.lookApp.id
    text: str = ""


class LookAppMsgParser(IMsgParser):
    """Парсер для Cellappmgr::lookApp."""

    def parse(self, msg: Message) -> LookAppMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = LookAppParsedMsgData(*values)
        return LookAppMsgParserResult(True, pd)


@dataclass
class UpdateCellappParsedMsgData(ParsedMsgData):
    """Данные Cellappmgr::updateCellapp."""

    componentID: KBEComponentId
    numEntities: KBEEntityId
    load: float
    flags: int


@dataclass(frozen=True)
class UpdateCellappMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::updateCellapp."""

    success: bool
    result: UpdateCellappParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.updateCellapp.id
    text: str = ""


class UpdateCellappMsgParser(IMsgParser):
    """Парсер для Cellappmgr::updateCellapp."""

    def parse(self, msg: Message) -> UpdateCellappMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = UpdateCellappParsedMsgData(*values)
        return UpdateCellappMsgParserResult(True, pd)


@dataclass
class UpdateSpaceDataParsedMsgData(ParsedMsgData):
    """Данные Cellappmgr::updateSpaceData."""

    componentID: KBEComponentId
    spaceID: KBESpaceId
    scriptModuleName: str
    delspace: bool
    geomappingPath: str


@dataclass(frozen=True)
class UpdateSpaceDataMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::updateSpaceData."""

    success: bool
    result: UpdateSpaceDataParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.updateSpaceData.id
    text: str = ""


class UpdateSpaceDataMsgParser(IMsgParser):
    """Парсер для Cellappmgr::updateSpaceData."""

    def parse(self, msg: Message) -> UpdateSpaceDataMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = UpdateSpaceDataParsedMsgData(*values)
        return UpdateSpaceDataMsgParserResult(True, pd)


@dataclass(frozen=True)
class ReqCreateCellEntityInNewSpaceMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::reqCreateCellEntityInNewSpace."""

    success: bool
    result: CreateCellEntityInNewSpaceFromBaseappParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.reqCreateCellEntityInNewSpace.id
    text: str = ""


class ReqCreateCellEntityInNewSpaceMsgParser(IMsgParser):
    """Парсер для Cellappmgr::reqCreateCellEntityInNewSpace."""

    def parse(
        self, msg: Message
    ) -> ReqCreateCellEntityInNewSpaceMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = CreateCellEntityInNewSpaceFromBaseappParser().parse(msg)
        return ReqCreateCellEntityInNewSpaceMsgParserResult(True, pd)


@dataclass
class OnCellappInitProgressParsedMsgData(ParsedMsgData):
    """Данные Cellappmgr::onCellappInitProgress."""

    cid: KBEComponentId  # COMPONENT_ID
    progress: float  # Прогресс инициализации (0.0-1.0)
    componentGlobalOrder: KBEComponentOrderId  # глобальный порядок
    componentGroupOrder: KBEComponentOrderId  # порядок в группе


@dataclass(frozen=True)
class OnCellappInitProgressMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::onCellappInitProgress."""

    success: bool
    result: OnCellappInitProgressParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.onCellappInitProgress.id
    text: str = ""


class OnCellappInitProgressMsgParser(IMsgParser):
    """Парсер для Cellappmgr::onCellappInitProgress."""

    def parse(self, msg: Message) -> OnCellappInitProgressMsgParserResult:
        """Обработка сообщения о прогрессе инициализации CellappMgr."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnCellappInitProgressParsedMsgData(*values)
        return OnCellappInitProgressMsgParserResult(True, pd)


@dataclass
class OnLookAppParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Cellappmgr::onLookApp."""

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
    """Парсер для Cellappmgr::onLookApp."""

    success: bool
    result: OnLookAppParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.onLookApp.id
    text: str = ""


class OnLookAppMsgParser(IMsgParser):
    """Парсер для Cellappmgr::onLookApp."""

    def parse(self, msg: Message) -> OnLookAppParserMsgParserResult:
        """Распарсить сообщение Cellappmgr::onLookApp.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnLookAppParserMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnLookAppParsedMsgData(*values)
        return OnLookAppParserMsgParserResult(success=True, result=pd)


@dataclass
class QueryLoadParsedMsgData(ParsedMsgData):
    """Данные Cellappmgr::queryLoad."""

    componentID: KBEComponentId
    componentType: str


@dataclass(frozen=True)
class QueryLoadMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::queryLoad."""

    success: bool
    result: QueryLoadParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.queryLoad.id
    text: str = ""


class QueryLoadMsgParser(IMsgParser):
    """Парсер для Cellappmgr::queryLoad."""

    def parse(self, msg: Message) -> QueryLoadMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = QueryLoadParsedMsgData(*values)
        return QueryLoadMsgParserResult(True, pd)


@dataclass
class ReqRestoreSpaceInCellParsedMsgData(ParsedMsgData):
    """Данные Cellappmgr::reqRestoreSpaceInCell."""

    componentID: KBEComponentId
    spaceID: KBESpaceId
    scriptModuleName: str


@dataclass(frozen=True)
class ReqRestoreSpaceInCellMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::reqRestoreSpaceInCell."""

    success: bool
    result: ReqRestoreSpaceInCellParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.reqRestoreSpaceInCell.id
    text: str = ""


class ReqRestoreSpaceInCellMsgParser(IMsgParser):
    """Парсер для Cellappmgr::reqRestoreSpaceInCell."""

    def parse(self, msg: Message) -> ReqRestoreSpaceInCellMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ReqRestoreSpaceInCellParsedMsgData(*values)
        return ReqRestoreSpaceInCellMsgParserResult(True, pd)


@dataclass
class ForwardMessageParsedMsgData(ParsedMsgData):
    """Данные Cellappmgr::forwardMessage."""

    targetComponentID: KBEComponentId
    msgID: int
    msgLength: int
    msgData: bytes


@dataclass(frozen=True)
class ForwardMessageMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::forwardMessage."""

    success: bool
    result: ForwardMessageParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.forwardMessage.id
    text: str = ""


class ForwardMessageMsgParser(IMsgParser):
    """Парсер для Cellappmgr::forwardMessage."""

    def parse(self, msg: Message) -> ForwardMessageMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = ForwardMessageParsedMsgData(*values)
        return ForwardMessageMsgParserResult(True, pd)


@dataclass
class StartProfileParsedMsgData(ParsedMsgData):
    """Данные Cellappmgr::startProfile."""

    profileName: KBEString  # noqa: N815  # pylint: disable=invalid-name
    profileType: KBEInt8  # noqa: N815  # pylint: disable=invalid-name
    timelen: KBEUInt32


@dataclass(frozen=True)
class StartProfileMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::startProfile."""

    success: bool
    result: StartProfileParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.startProfile.id
    text: str = ""


class StartProfileMsgParser(IMsgParser):
    """Парсер для Cellappmgr::startProfile."""

    def parse(self, msg: Message) -> StartProfileMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = StartProfileParsedMsgData(*values)
        return StartProfileMsgParserResult(True, pd)


@dataclass
class ReqKillServerParsedMsgData(ParsedMsgData):
    """Данные Cellappmgr::reqKillServer."""

    # Сообщение не содержит аргументов


@dataclass(frozen=True)
class ReqKillServerMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::reqKillServer."""

    success: bool
    result: ReqKillServerParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.reqKillServer.id
    text: str = ""


class ReqKillServerMsgParser(IMsgParser):
    """Парсер для Cellappmgr::reqKillServer."""

    def parse(self, msg: Message) -> ReqKillServerMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        pd = ReqKillServerParsedMsgData()
        return ReqKillServerMsgParserResult(True, pd)


@dataclass
class QueryWatcherParsedMsgData(ParsedMsgData):
    """Данные Cellappmgr::queryWatcher."""

    componentType: KBEComponentType
    componentID: KBEComponentId
    uid: int
    username: str
    watcherPath: str


@dataclass(frozen=True)
class QueryWatcherMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::queryWatcher."""

    success: bool
    result: QueryWatcherParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.queryWatcher.id
    text: str = ""


class QueryWatcherMsgParser(IMsgParser):
    """Парсер для Cellappmgr::queryWatcher."""

    def parse(self, msg: Message) -> QueryWatcherMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = QueryWatcherParsedMsgData(*values)
        return QueryWatcherMsgParserResult(True, pd)


@dataclass
class QueryAppsLoadsParsedMsgData(ParsedMsgData):
    """Данные Cellappmgr::queryAppsLoads."""

    componentType: KBEComponentType
    componentID: KBEComponentId
    uid: int
    username: str


@dataclass(frozen=True)
class QueryAppsLoadsMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::queryAppsLoads."""

    success: bool
    result: QueryAppsLoadsParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.queryAppsLoads.id
    text: str = ""


class QueryAppsLoadsMsgParser(IMsgParser):
    """Парсер для Cellappmgr::queryAppsLoads."""

    def parse(self, msg: Message) -> QueryAppsLoadsMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = QueryAppsLoadsParsedMsgData(*values)
        return QueryAppsLoadsMsgParserResult(True, pd)


@dataclass
class QuerySpacesParsedMsgData(ParsedMsgData):
    """Данные Cellappmgr::querySpaces."""

    componentType: KBEComponentType
    componentID: KBEComponentId
    uid: int
    username: str


@dataclass(frozen=True)
class QuerySpacesMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::querySpaces."""

    success: bool
    result: QuerySpacesParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.querySpaces.id
    text: str = ""


class QuerySpacesMsgParser(IMsgParser):
    """Парсер для Cellappmgr::querySpaces."""

    def parse(self, msg: Message) -> QuerySpacesMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = QuerySpacesParsedMsgData(*values)
        return QuerySpacesMsgParserResult(True, pd)


@dataclass
class SetSpaceViewerParsedMsgData(ParsedMsgData):
    """Данные Cellappmgr::setSpaceViewer."""

    componentType: KBEComponentType
    componentID: KBEComponentId
    uid: int
    username: str
    spaceID: KBESpaceId
    viewerID: KBEEntityId


@dataclass(frozen=True)
class SetSpaceViewerMsgParserResult(MsgParserResult):
    """Результат парсинга Cellappmgr::setSpaceViewer."""

    success: bool
    result: SetSpaceViewerParsedMsgData | None
    msg_id: int = msgspec.cellappmgr.setSpaceViewer.id
    text: str = ""


class SetSpaceViewerMsgParser(IMsgParser):
    """Парсер для Cellappmgr::setSpaceViewer."""

    def parse(self, msg: Message) -> SetSpaceViewerMsgParserResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = SetSpaceViewerParsedMsgData(*values)
        return SetSpaceViewerMsgParserResult(True, pd)
