"""Парсеры сообщений о состоянии SpaceData (глобальное состояние space)."""

import logging
from dataclasses import dataclass
from typing import Any, TypeAlias

from enki import msgspec
from enki.kbetype.decoders.basic_data_type_decoders import STRING
from enki.kbetype.decoders.custom_decoders import (
    SPACE_ID,
)
from enki.misc import devonly
from enki.msg.message import Message
from enki.msg_parser.imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

logger = logging.getLogger(__name__)

PositiveInt: TypeAlias = int
SpaceDataSpaceId: TypeAlias = PositiveInt
SpaceDataKey: TypeAlias = str
SpaceDataValue: TypeAlias = str


@dataclass
class InitSpaceDataParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения initSpaceData.

    Attributes:
        space_id: Идентификатор пространства
        pairs: Словарь пар ключ-значение с данными пространства

    """

    space_id: SpaceDataSpaceId
    pairs: dict[SpaceDataKey, SpaceDataValue]


@dataclass
class InitSpaceDataMsgParserResult(MsgParserResult):
    """Результат парсинга сообщения initSpaceData.

    Attributes:
        msg_id: Идентификатор сообщения
        result: Распарсенные данные сообщения

    """

    msg_id: int = msgspec.client.initSpaceData.id
    result: InitSpaceDataParsedMsgData


class InitSpaceDataParser(IMsgParser):
    """Парсер сообщения initSpaceData."""

    def parse(self, msg: Message) -> InitSpaceDataMsgParserResult:
        """Разобрать сообщение initSpaceData.

        Args:
            msg: Сообщение для разбора

        Returns:
            InitSpaceDataMsgParserResult: Результат парсинга, содержащий:
                - space_id: идентификатор пространства
                - pairs: словарь с данными пространства

        Raises:
            ValueError: Если данные сообщения некорректны

        """
        logger.debug("[%s] (%s)", self, devonly.func_args_values())

        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])

        space_id, offset = SPACE_ID.decode(data)
        data = data[offset:]

        pairs: dict[SpaceDataKey, SpaceDataValue] = {}

        while data:
            key, offset = STRING.decode(data)
            data = data[offset:]
            value, offset = STRING.decode(data)
            data = data[offset:]

            pairs[SpaceDataKey(key)] = SpaceDataValue(value)

        pd = InitSpaceDataParsedMsgData(SpaceDataSpaceId(space_id), pairs)
        return InitSpaceDataMsgParserResult(success=True, result=pd)


@dataclass
class SetSpaceDataParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения setSpaceData.

    Attributes:
        space_id: Идентификатор пространства
        key: Ключ данных
        value: Значение данных

    """

    space_id: SpaceDataSpaceId
    key: SpaceDataKey
    value: SpaceDataValue


@dataclass
class SetSpaceDataMsgParserResult(MsgParserResult):
    """Результат парсинга сообщения setSpaceData.

    Attributes:
        result: Распарсенные данные сообщения
        msg_id: Идентификатор сообщения

    """

    result: SetSpaceDataParsedMsgData
    msg_id: int = msgspec.client.setSpaceData.id


class SetSpaceDataParser(IMsgParser):
    """Парсер сообщения setSpaceData."""

    def parse(self, msg: Message) -> SetSpaceDataMsgParserResult:
        """Разобрать сообщение setSpaceData.

        Args:
            msg: Сообщение для разбора

        Returns:
            SetSpaceDataMsgParserResult: Результат парсинга, содержащий:
                - space_id: идентификатор пространства
                - key: ключ данных
                - value: значение данных

        """
        logger.debug("[%s] (%s)", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        space_id = SpaceDataSpaceId(values[0])
        key = SpaceDataKey(values[1])
        value = SpaceDataValue(values[2])
        pd = SetSpaceDataParsedMsgData(space_id, key, value)
        return SetSpaceDataMsgParserResult(success=True, result=pd)


@dataclass
class DelSpaceDataParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения delSpaceData.

    Attributes:
        space_id: Идентификатор пространства
        key: Ключ удаляемых данных

    """

    space_id: SpaceDataSpaceId
    key: SpaceDataKey


@dataclass
class DelSpaceDataMsgParserResult(MsgParserResult):
    """Результат парсинга сообщения delSpaceData.

    Attributes:
        result: Распарсенные данные сообщения
        msg_id: Идентификатор сообщения

    """

    result: DelSpaceDataParsedMsgData
    msg_id: int = msgspec.client.delSpaceData.id


class DelSpaceDataParser(IMsgParser):
    """Парсер сообщения delSpaceData."""

    def parse(self, msg: Message) -> DelSpaceDataMsgParserResult:
        """Разобрать сообщение delSpaceData.

        Args:
            msg: Сообщение для разбора

        Returns:
            DelSpaceDataMsgParserResult: Результат парсинга, содержащий:
                - space_id: идентификатор пространства
                - key: ключ удаляемых данных

        """
        logger.debug("[%s] (%s)", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        space_id = SpaceDataSpaceId(values[0])
        key = SpaceDataKey(values[1])
        pd = DelSpaceDataParsedMsgData(space_id, key)
        return DelSpaceDataMsgParserResult(success=True, result=pd)
