"""Обработчик сообщений для компонента Client."""

import logging
from dataclasses import dataclass
from typing import Type
from enki import settings

from enki.core import kbemath, kbetype, msgspec
from enki.core.enkitype import AppAddr
from enki.core.kbeenum import ServerError
from enki.core.message import Message
from enki.misc import devonly

from .base import ParsedMsgData, HandlerResult, Handler
from .serverhandler.common import OnRegisterNewAppParsedData


logger = logging.getLogger(__file__)



@dataclass
class OnLoginSuccessfullyParsedData(ParsedMsgData):
    account_name: str = ''
    host: str = ''
    tcp_port: int = 0
    udp_port: int = 0
    data: bytes = b''

    @property
    def tcp_address(self) -> AppAddr:
        return AppAddr(self.host, self.tcp_port)

    @property
    def udp_address(self) -> AppAddr:
        return AppAddr(self.host, self.udp_port)

    __add_to_dict__ = [
        'tcp_address', 'udp_address'
    ]


@dataclass
class OnLoginSuccessfullyHandlerResult(HandlerResult):
    success: bool
    result: OnLoginSuccessfullyParsedData
    msg_id: int = msgspec.app.client.onLoginSuccessfully.id
    text: str = ''


class OnLoginSuccessfullyHandler(Handler):
    """Обработчик для Client::onLoginSuccessfully."""

    def handle(self, msg: Message) -> OnLoginSuccessfullyHandlerResult:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        data: memoryview = msg.get_values()[0]
        pd = OnLoginSuccessfullyParsedData()
        pd.account_name, offset = kbetype.STRING.decode(data)
        data = data[offset:]
        pd.host, offset = kbetype.STRING.decode(data)
        data = data[offset:]
        pd.tcp_port, offset = kbetype.UINT16.decode(data)
        data = data[offset:]
        if settings.KBE_VERSION == 2:
            pd.udp_port, offset = kbetype.UINT16.decode(data)
            data = data[offset:]
        pd.data, offset = kbetype.BLOB.decode(data)
        data = data[offset:]
        return OnLoginSuccessfullyHandlerResult(True, pd)


CLIENT_HANDLERS: dict[int, Type[Handler]] = {
    msgspec.app.client.onLoginSuccessfully.id: OnLoginSuccessfullyHandler
}
