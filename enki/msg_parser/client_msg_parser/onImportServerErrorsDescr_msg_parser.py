"""Обработчик сообщений для компонента Client."""

import logging
from dataclasses import dataclass
from typing import Any

from enki import msgspec
from enki.kbetype.decoders.basic_data_type_decoders import (
    BLOB,
    INT16,
    UINT16,
)
from enki.misc import devonly
from enki.msg.message import Message
from enki.msg_parser.imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData

logger = logging.getLogger(__name__)


@dataclass
class ParsedServerErrorInfo:
    """Данные распарсенных ошибок сервера."""

    id: int
    name: str
    desc: str


@dataclass
class OnImportServerErrorsDescrParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения BaseappMgr::onImportServerErrorsDescr."""

    server_error_infos: list[ParsedServerErrorInfo]


@dataclass(frozen=True)
class OnImportServerErrorsDescrMsgParserResult(MsgParserResult):
    """Парсер для BaseappMgr::onImportServerErrorsDescr."""

    success: bool
    result: OnImportServerErrorsDescrParsedMsgData
    msg_id: int = msgspec.client.onImportServerErrorsDescr.id
    text: str = ""


class OnImportServerErrorsDescrMsgParser(IMsgParser):
    """Парсер для BaseappMgr::onImportServerErrorsDescr."""

    def parse(self, msg: Message) -> OnImportServerErrorsDescrMsgParserResult:
        """Распарсить сообщение BaseappMgr::onImportServerErrorsDescr.

        Args:
            msg (Message): KBEngine-сообщение

        Returns:
            OnImportServerErrorsDescrParserMsgParserResult: объект
                результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])

        size, shift = UINT16.decode(data)
        data = data[shift:]

        specs = []
        for _ in range(size):
            err_id, offset = INT16.decode(data)
            data = data[offset:]

            name, offset = BLOB.decode(data)
            data = data[offset:]

            desc, offset = BLOB.decode(data)
            data = data[offset:]

            specs.append(
                ParsedServerErrorInfo(
                    err_id,
                    name=name.decode(),
                    desc=desc.decode(),
                )
            )

        pd = OnImportServerErrorsDescrParsedMsgData(specs)
        return OnImportServerErrorsDescrMsgParserResult(success=True, result=pd)
