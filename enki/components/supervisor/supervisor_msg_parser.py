"""Обработчик сообщений компонента Supervisor (расширение Machine)."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from enki.components.imsg_parser import IMsgParser, MsgParserResult, ParsedMsgData
from enki.kbetype import KBEUInt64
from enki.kbetype.decoders.custom_decoders import KBEComponentId  # noqa: TC001
from enki.misc import devonly
from enki.msg import msgspec
from enki.msg.message import Message  # noqa: TC001

logger = logging.getLogger(__file__)


@dataclass
class OnStopComponentParsedData(ParsedMsgData):
    """Распарсенные данные соощения Supervisor::OnStopComponent."""

    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name


@dataclass
class OnStopComponentMsgResult(MsgParserResult):
    """Результат парсинга сообщения Supervisor::OnStopComponent."""

    success: bool
    result: OnStopComponentParsedData
    msg_id: int = msgspec.supervisor.onStopComponent.id
    text: str = ""


class OnStopComponentMsgParser(IMsgParser):
    """Парсер для Supervisor::OnStopComponent."""

    def parse(self, msg: Message) -> OnStopComponentMsgResult:
        """Распарсить сообщение Supervisor::OnStopComponent.

        Args:
            msg (Message): KBEngine-сообщение

        Raises:
            TypeError: the message has an invalid value

        Returns:
            OnStopComponentMsgResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        component_id = msg.get_values()[0]
        # ComponentId — это алиас для KBEUInt64
        if not isinstance(component_id, KBEUInt64):
            err_text = (
                f"The message has an invalid value. Expected "
                f"ComponentId (KBEUInt64), got {type(component_id)}"
            )
            raise TypeError(err_text)

        pd = OnStopComponentParsedData(component_id)
        return OnStopComponentMsgResult(success=True, result=pd)
