"""Парсер сообщений от компонента Machine."""

from __future__ import annotations

import copy
import dataclasses
import json
import logging
import os
import pwd
from dataclasses import dataclass
from typing import Any, ClassVar, Self

from enki import msgspec
from enki.core import kbemath
from enki.kbeenum import ComponentType
from enki.kbetype.decoders.custom_decoders import (
    KBEComponentGusId,
    KBEComponentId,
    KBEComponentOrderId,
    KBEComponentType,
    KBECpu,
    KBEExtAddrEx,
    KBEExtraData,
    KBEIntAddr,
    KBEIntPort,
    KBEMachineId,
    KBEMacMd5,
    KBEMem,
    KBEPid,
    KBEStateId,
    KBEUid,
    KBEUsedMem,
    KBEUsername,
)
from enki.kbetype.pytypes.basic_data_types import KBEInt32
from enki.misc import devonly
from enki.msg.message import Message  # noqa: TC001
from enki.msg_parser.imsg_parser import (
    IMsgParser,
    MsgParserResult,
    ParsedMsgData,
)
from enki.net.addr import Addr, Port

logger = logging.getLogger(__name__)


@dataclass
class OnBroadcastInterfaceParsedData(ParsedMsgData):
    """Распарсенные данные сообщения Machine::onBroadcastInterface.

    Содержит информацию о компоненте, его сетевых адресах, состоянии и метаданных.
    Используется для обмена информацией между компонентами системы.
    """

    uid: KBEUid
    username: KBEUsername
    componentType: KBEComponentType  # noqa: N815  # pylint: disable=invalid-name
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    componentIDEx: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    globalorderid: KBEComponentOrderId
    grouporderid: KBEComponentOrderId
    gus: KBEComponentGusId
    intaddr: KBEIntAddr
    intport: KBEIntPort
    extaddr: KBEIntAddr
    extport: KBEIntPort
    extaddrEx: KBEExtAddrEx  # noqa: N815  # pylint: disable=invalid-name
    pid: KBEPid
    cpu: KBECpu
    mem: KBEMem
    usedmem: KBEUsedMem
    state: KBEStateId
    machineID: KBEMachineId  # noqa: N815  # pylint: disable=invalid-name
    extradata: KBEExtraData
    extradata1: KBEExtraData
    extradata2: KBEExtraData
    extradata3: KBEExtraData
    backRecvAddr: KBEIntAddr  # noqa: N815  # pylint: disable=invalid-name
    backRecvPort: KBEIntPort  # noqa: N815  # pylint: disable=invalid-name

    @staticmethod
    def get_empty() -> OnBroadcastInterfaceParsedData:
        """Создает и возвращает объект с пустыми/дефолтными значениями.

        Используется для создания объекта с минимально валидными значениями,
        когда требуется заполнить обязательные поля без реальных данных.

        Returns:
            OnBroadcastInterfaceParsedData: Объект с пустыми значениями полей:
                - uid и username берутся из текущего пользователя системы
                - componentType устанавливается в UNKNOWN_COMPONENT
                - числовые поля инициализируются нулями или -1
                - строковые поля - пустыми строками

        """
        return OnBroadcastInterfaceParsedData(
            uid=KBEUid(os.getuid()),
            username=KBEUsername(pwd.getpwuid(os.getuid())[0]),
            componentType=KBEComponentType(ComponentType.UNKNOWN_COMPONENT.value),
            componentID=KBEComponentId(0),
            componentIDEx=KBEComponentId(0),
            globalorderid=KBEComponentOrderId(-1),
            grouporderid=KBEComponentOrderId(-1),
            gus=KBEComponentGusId(-1),
            intaddr=KBEIntAddr(0),
            intport=KBEIntPort(0),
            extaddr=KBEIntAddr(0),
            extport=KBEIntPort(0),
            extaddrEx=KBEExtAddrEx(""),
            pid=KBEPid(0),
            cpu=KBECpu(0),
            mem=KBEMem(0),
            usedmem=KBEUsedMem(0),
            state=KBEStateId(0),
            machineID=KBEMachineId(1),
            extradata=KBEExtraData(0),
            extradata1=KBEExtraData(0),
            extradata2=KBEExtraData(0),
            extradata3=KBEExtraData(0),
            backRecvAddr=KBEIntAddr(0),
            backRecvPort=KBEIntPort(0),
        )

    def copy(self) -> OnBroadcastInterfaceParsedData:
        """Создает глубокую копию текущего объекта.

        Returns:
            OnBroadcastInterfaceParsedData: Полная копия текущего объекта

        """
        return copy.deepcopy(self)

    @staticmethod
    def to_json(pd: OnBroadcastInterfaceParsedData) -> str:
        """Сериализует объект в JSON строку.

        Args:
            pd: Объект для сериализации

        Returns:
            str: JSON представление объекта

        """
        return json.dumps(dataclasses.asdict(pd))

    @staticmethod
    def from_json(text: str) -> OnBroadcastInterfaceParsedData:
        """Десериализует объект из JSON строки.

        Args:
            text: JSON строка с данными объекта

        Returns:
            OnBroadcastInterfaceParsedData: Восстановленный объект

        """
        return OnBroadcastInterfaceParsedData(**json.loads(text))

    @property
    def component_type(self) -> ComponentType:
        """Возвращает тип компонента в виде enum ComponentType.

        Returns:
            ComponentType: Тип компонента

        """
        return ComponentType(self.componentType)

    @property
    def internal_address(self) -> Addr:
        """Возвращает внутренний адрес в виде объекта Addr.

        Returns:
            Addr: Объект с host и port внутреннего адреса

        """
        return Addr(
            kbemath.int2ip(self.intaddr), Port(kbemath.int2port(self.intport))
        )

    @property
    def external_address(self) -> Addr:
        """Возвращает внешний адрес в виде объекта Addr.

        Returns:
            Addr: Объект с host и port внешнего адреса

        """
        return Addr(
            kbemath.int2ip(self.extaddr), Port(kbemath.int2port(self.extport))
        )

    @property
    def callback_address(self) -> Addr:
        """Возвращает адрес для callback вызовов.

        Returns:
            Addr: Объект с host и port callback адреса

        """
        return Addr(
            kbemath.int2ip(self.backRecvAddr),
            Port(kbemath.int2port(self.backRecvPort)),
        )

    @callback_address.setter
    def callback_address(self, addr: Addr) -> None:
        """Устанавливает callback адрес.

        Args:
            addr: Новый адрес в виде объекта Addr

        """
        self.backRecvAddr = KBEIntAddr(kbemath.ip2int(addr.ip_addr))
        self.backRecvPort = KBEIntPort(kbemath.port2int(addr.port))

    __add_to_dict__: ClassVar = [
        "component_type",
        "internal_address",
        "external_address",
        "callback_address",
    ]


@dataclass
class OnBroadcastInterfaceMsgParserResult(MsgParserResult):
    """Результат парсинга сообщения для Machine::onBroadcastInterface."""

    success: bool
    result: OnBroadcastInterfaceParsedData
    msg_id: int = msgspec.machine.onBroadcastInterface.id
    text: str = ""


class OnBroadcastInterfaceMsgParser(IMsgParser):
    """Парсер сообщения Machine::onBroadcastInterface."""

    def parse(self, msg: Message) -> OnBroadcastInterfaceMsgParserResult:
        """Распарсить сообщение Machine::onBroadcastInterface.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnBroadcastInterfaceMsgResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: Any = msg.get_values()
        pd = OnBroadcastInterfaceParsedData(*values)
        return OnBroadcastInterfaceMsgParserResult(success=True, result=pd)


@dataclass
class OnFindInterfaceAddrParsedData(ParsedMsgData):
    """Распарсенные данные сообщения Machine::onFindInterfaceAddr.

    Содержит информацию для поиска адреса компонента.
    """

    uid: KBEUid
    username: KBEUsername
    componentType: KBEComponentType  # noqa: N815  # pylint: disable=invalid-name
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    findComponentType: KBEComponentType  # noqa: N815  # pylint: disable=invalid-name
    finderAddr: KBEIntAddr  # noqa: N815  # pylint: disable=invalid-name
    finderRecvPort: KBEIntPort  # noqa: N815  # pylint: disable=invalid-name

    @classmethod
    def get_empty(cls) -> Self:
        """Создает и возвращает объект с пустыми/дефолтными значениями.

        Используется для создания объекта с минимально валидными значениями,
        когда требуется заполнить обязательные поля без реальных данных.

        Returns:
            OnFindInterfaceAddrParsedData: Объект с пустыми значениями полей

        """
        return cls(
            uid=KBEUid(1000),
            username=KBEUsername("root"),
            componentType=KBEComponentType(ComponentType.UNKNOWN_COMPONENT),
            componentID=KBEComponentId(0),
            findComponentType=KBEComponentType(ComponentType.UNKNOWN_COMPONENT),
            finderAddr=KBEIntAddr(0),
            finderRecvPort=KBEIntPort(Port.get_no_port_obj()),
        )

    @property
    def component_type(self) -> ComponentType:
        """Возвращает тип компонента в виде enum ComponentType.

        Returns:
            ComponentType: Тип текущего компонента

        """
        return ComponentType(self.componentType)

    @property
    def callback_address(self) -> Addr:
        """Возвращает адрес для callback вызовов.

        Returns:
            Addr: Объект с host и port callback адреса

        """
        return Addr(
            kbemath.int2ip(self.finderAddr),
            Port(kbemath.int2port(self.finderRecvPort)),
        )

    @callback_address.setter
    def callback_address(self, addr: Addr) -> None:
        """Устанавливает callback адрес.

        Args:
            addr: Новый адрес в виде объекта Addr

        """
        self.finderAddr = KBEIntAddr(kbemath.ip2int(addr.ip_addr))
        self.finderRecvPort = KBEIntPort(kbemath.port2int(addr.port))

    @property
    def find_component_type(self) -> ComponentType:
        """Возвращает тип компонента, который нужно найти.

        Returns:
            ComponentType: Тип искомого компонента или UNKNOWN_COMPONENT при ошибке

        """
        try:
            return ComponentType(self.findComponentType)
        except ValueError:
            return ComponentType.UNKNOWN_COMPONENT

    @find_component_type.setter
    def find_component_type(self, comp_type: ComponentType) -> None:
        self.findComponentType = KBEComponentType(comp_type.value)

    @property
    def find_component_id(self) -> int:
        return self.componentID

    @find_component_id.setter
    def find_component_id(self, value: int) -> None:
        self.componentID = KBEComponentId(value)

    __add_to_dict__: ClassVar = (
        "component_type",
        "callback_address",
        "find_component_type",
    )


@dataclass
class OnFindInterfaceAddrMsgParserResult(MsgParserResult):
    """Результат парсинга для Machine::onFindInterfaceAddr."""

    success: bool
    result: OnFindInterfaceAddrParsedData
    msg_id: int = msgspec.machine.onFindInterfaceAddr.id
    text: str = ""


class OnFindInterfaceAddrMsgParser(IMsgParser):
    """Парсер для Machine::onFindInterfaceAddr."""

    def parse(self, msg: Message) -> OnFindInterfaceAddrMsgParserResult:
        """Распарсить сообщение Machine::onFindInterfaceAddr.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnFindInterfaceAddrMsgResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnFindInterfaceAddrParsedData(*values)
        return OnFindInterfaceAddrMsgParserResult(success=True, result=pd)


@dataclass
class QueryComponentIDParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Machine::queryComponentID."""

    componentType: KBEComponentType  # noqa: N815  # pylint: disable=invalid-name
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    uid: KBEUid
    finderRecvPort: KBEIntPort  # noqa: N815  # pylint: disable=invalid-name
    macMD5: KBEMacMd5  # noqa: N815  # pylint: disable=invalid-name
    pid: KBEInt32

    @classmethod
    def get_empty(cls) -> Self:
        """Создает и возвращает объект с пустыми/дефолтными значениями.

        Используется для создания объекта с минимально валидными значениями,
        когда требуется заполнить обязательные поля без реальных данных.

        Returns:
            OnBroadcastInterfaceParsedData: Объект с пустыми значениями полей:
                - uid и username берутся из текущего пользователя системы
                - componentType устанавливается в UNKNOWN_COMPONENT
                - числовые поля инициализируются нулями или -1
                - строковые поля - пустыми строками

        """
        return cls(
            componentType=KBEComponentType(ComponentType.UNKNOWN_COMPONENT.value),
            componentID=KBEComponentId(0),
            uid=KBEUid(0),
            finderRecvPort=KBEIntPort(Port.get_no_port_obj()),
            macMD5=KBEMacMd5(0),
            pid=KBEInt32(0),
        )

    @property
    def component_type(self) -> ComponentType:
        """Возвращает тип компонента в виде enum ComponentType.

        Returns:
            ComponentType: Тип текущего компонента

        """
        return ComponentType(self.componentType)

    @property
    def callback_port(self) -> int:
        """Возвращает порт для callback вызовов.

        Returns:
            int: Номер порта в читаемом формате

        """
        return kbemath.int2port(self.finderRecvPort)

    @callback_port.setter
    def callback_port(self, value: int) -> None:
        """Устанавливает порт для callback вызовов.

        Args:
            value: Номер порта в читаемом формате

        """
        self.finderRecvPort = KBEIntPort(kbemath.port2int(value))

    __add_to_dict__: ClassVar = ("component_type", "callback_port")


@dataclass
class QueryComponentIDParserMsgResult(MsgParserResult):
    """Парсер для Machine::queryComponentID."""

    success: bool
    result: QueryComponentIDParsedMsgData | None
    msg_id: int = msgspec.machine.queryComponentID.id
    text: str = ""


class QueryComponentIDMsgParser(IMsgParser):
    """Парсер для Machine::queryComponentID."""

    def parse(self, msg: Message) -> QueryComponentIDParserMsgResult:
        """Распарсить сообщение Machine::queryComponentID.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnFindInterfaceAddrMsgResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = QueryComponentIDParsedMsgData(*values)
        return QueryComponentIDParserMsgResult(success=True, result=pd)


@dataclass
class OnQueryAllInterfaceInfosParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Machine::onQueryAllInterfaceInfos."""

    uid: KBEUid
    username: KBEUsername
    finderRecvPort: KBEIntPort  # noqa: N815  # pylint: disable=invalid-name

    @property
    def callback_port(self) -> Port:
        """Возвращает порт для callback вызовов.

        Returns:
            int: Номер порта в читаемом формате

        """
        return Port(kbemath.int2port(self.finderRecvPort))

    @callback_port.setter
    def callback_port(self, value: int) -> None:
        """Устанавливает порт для callback вызовов.

        Args:
            value: Номер порта в читаемом формате

        """
        self.finderRecvPort = KBEIntPort(kbemath.port2int(value))

    __add_to_dict__: ClassVar = ("callback_port",)


@dataclass
class OnQueryAllInterfaceInfosParserMsgResult(MsgParserResult):
    """Парсер для Machine::onQueryAllInterfaceInfos."""

    success: bool
    result: OnQueryAllInterfaceInfosParsedMsgData
    msg_id: int = msgspec.machine.onQueryAllInterfaceInfos.id
    text: str = ""


class OnQueryAllInterfaceInfosMsgParser(IMsgParser):
    """Парсер для Machine::onQueryAllInterfaceInfos."""

    def parse(self, msg: Message) -> OnQueryAllInterfaceInfosParserMsgResult:
        """Распарсить сообщение Machine::onQueryAllInterfaceInfos.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnQueryAllInterfaceInfosParserMsgResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = OnQueryAllInterfaceInfosParsedMsgData(*values)
        return OnQueryAllInterfaceInfosParserMsgResult(success=True, result=pd)
