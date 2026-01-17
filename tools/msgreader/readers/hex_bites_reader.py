"""Чтение сериализованного сообщения представленного в виде 16-ых байтов."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias

from enki.misc.result import Result

from .deserializers import (
    deserialize_msg,
    deserialize_msg_id,
    deserialize_msg_without_id_and_len,
)

if TYPE_CHECKING:
    from enki.kbeenum import ComponentType
    from enki.msg.message import Message
    from enki.msg.msg_descr import MsgId

logger = logging.getLogger(__name__)


UnReadedData: TypeAlias = bytes


@dataclass(frozen=True)
class HexBitesReaderResultData:
    """Данные, описывающие удачный или неудачный результат чтения сообщения."""

    msg: Message | None
    data_tail: UnReadedData


@dataclass(frozen=True)
class HexBitesReaderResult(Result):
    """Данные, описывающие удачный или неудачный результат чтения сообщения."""

    success: bool
    result: HexBitesReaderResultData
    text: str = ""


@dataclass(frozen=True)
class HexBitesMsgIdReaderResultData:
    """Данные, описывающие удачный или неудачный результат чтения сообщения."""

    msg_id: MsgId | None
    data_tail: UnReadedData


@dataclass(frozen=True)
class HexBitesMsgIdReaderResult(Result):
    """Удачный или неудачный результат чтения id сообщения."""

    success: bool
    result: HexBitesMsgIdReaderResultData
    text: str = ""


class HexBitesReader:
    """Чтение сериализованного сообщения представленного в виде 16-ых байтов."""

    def read_data(
        self,
        hex_data: str,
        no_envelop_msg_name: str | None,
        comp_type: ComponentType,
    ) -> HexBitesReaderResult:
        """Прочитать сериализованное сообщение."""
        if no_envelop_msg_name is not None:
            res = deserialize_msg_without_id_and_len(
                hex_data, no_envelop_msg_name
            )
        else:
            res = deserialize_msg(hex_data, comp_type)

        if not res.success:
            text = f"The message cannot be deserialized (reason = '{res.text}')"
            logger.error(text)
            return HexBitesReaderResult(
                success=False,
                result=HexBitesReaderResultData(None, hex_data.encode()),
                text=text,
            )

        assert res.result is not None
        msg = res.result.msg
        assert msg is not None

        return HexBitesReaderResult(
            success=True,
            result=HexBitesReaderResultData(msg, res.result.data_tail),
        )

    def read_msg_id(self, hex_data: str) -> HexBitesMsgIdReaderResult:
        """Прочитать id сериализованного сообщения."""
        res = deserialize_msg_id(hex_data)
        if not res.success:
            text = f"The message id cannot be deserialize . The reason is '{res.text}'"
            logger.error(text)
            return HexBitesMsgIdReaderResult(
                success=False,
                result=HexBitesMsgIdReaderResultData(None, hex_data.encode()),
                text=text,
            )

        assert res.result is not None
        msg_id = res.result.msg_id
        assert msg_id is not None
        logger.debug("The message id is '%s'", msg_id)

        return HexBitesMsgIdReaderResult(
            success=True,
            result=HexBitesMsgIdReaderResultData(msg_id, res.result.data_tail),
        )
