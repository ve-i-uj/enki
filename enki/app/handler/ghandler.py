"""General handlers."""

from dataclasses import dataclass
from enki.net import msgspec
from enki.kbeenum import ServerError
from . import base

from enki.net.kbeclient import Message

from enki.app.iapp import IApp


@dataclass
class OnKickedHandlerParsedData(base.ParsedMsgData):
    ret_code: ServerError


@dataclass
class OnKickedHandlerResult(base.HandlerResult):
    success: bool
    result: OnKickedHandlerParsedData
    msg_id: int = msgspec.app.client.onKicked.id
    text: str = ''


class OnKickedHandler(base.Handler):

    def __init__(self, app: IApp) -> None:
        super().__init__()
        self._app = app

    def handle(self, msg: Message) -> OnKickedHandlerResult:
        code: int = msg.get_values()[0]
        server_error = ServerError(code)
        return OnKickedHandlerResult(True, OnKickedHandlerParsedData(server_error))
