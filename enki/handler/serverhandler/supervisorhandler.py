"""Обработчик сообщений от компонента Supervisor."""

from __future__ import annotations

import copy
import dataclasses
import json
import os
import logging
from dataclasses import dataclass
import pwd
from typing import Optional

from enki.core import kbemath
from enki.core.enkitype import AppAddr
from enki.core import msgspec
from enki.core.kbeenum import ComponentType
from enki.core.message import Message
from enki.misc import devonly

from ..base import ParsedMsgData, Handler, HandlerResult

logger = logging.getLogger(__file__)


@dataclass
class OnStopComponentParsedData(ParsedMsgData):
    componentID: int


@dataclass
class OnStopComponentHandlerResult(HandlerResult):
    """Обработчик для Supervisor::OnStopComponent."""
    success: bool
    result: OnStopComponentParsedData
    msg_id: int = msgspec.app.supervisor.onStopComponent.id
    text: str = ''


class OnStopComponentHandler(Handler):

    def handle(self, msg: Message) -> OnStopComponentHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnStopComponentParsedData(*msg.get_values())
        return OnStopComponentHandlerResult(True, pd)
