"""Обработчик сообщений от компонента DBMgr."""

import logging
from dataclasses import dataclass

from enki.core import kbeenum, kbemath
from enki.core import enkitype
from enki.core import msgspec
from enki.core.message import Message
from enki.misc import devonly

from ..base import ParsedMsgData, HandlerResult, Handler
from .common import OnAppActiveTickParsedData

logger = logging.getLogger(__file__)


@dataclass
class OnAppActiveTickHandlerResult(HandlerResult):
    """Обработчик для DBMgr::onAppActiveTick."""
    success: bool
    result: OnAppActiveTickParsedData
    msg_id: int = msgspec.app.cellappmgr.onAppActiveTick.id
    text: str = ''


class OnAppActiveTickHandler(Handler):

    def handle(self, msg: Message) -> OnAppActiveTickHandlerResult:
        """Handle a message."""
        logger.debug('[%s] %s', self, devonly.func_args_values())
        pd = OnAppActiveTickParsedData(*msg.get_values())
        return OnAppActiveTickHandlerResult(True, pd)
