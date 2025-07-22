"""Entity message handlers."""

import logging
from dataclasses import dataclass

from enki.app.clientapp.layer import ilayer
from enki.app.clientapp.layer.thlayer import IGameLayer
from enki.core import kbetype, msgspec
from enki.core.message import Message
from enki.core.novalue import NoValue
from enki.handlers.base import Handler, MsgResult, ParsedMsgInfo
from enki.misc import devonly

logger = logging.getLogger(__name__)


class SpaceDataMgr:
    @property
    def _game_layer(self) -> IGameLayer:
        return ilayer.get_game_layer()

    def set_data(self, space_id: int, key: str, value: str):
        self._game_layer.call_set_space_data(space_id, key, value)

    def del_data(self, space_id: int, key: str):
        self._game_layer.call_delete_space_data(space_id, key)


class SpaceDataMsgParser(IMsgParser):
    def __init__(self, space_data_mgr: SpaceDataMgr) -> None:
        self._space_data_mgr = space_data_mgr

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"


@dataclass
class InitSpaceDataParsedData(ParsedMsgInfo):
    space_id: int
    pairs: dict[str, str]


@dataclass
class InitSpaceDataHandlerResult(MsgResult):
    msg_id: int = msgspec.app.client.initSpaceData.id
    result: InitSpaceDataParsedData


class InitSpaceDataHandler(SpaceDataHandler):
    def parse(self, msg: Message) -> InitSpaceDataMsgResult:
        logger.debug(f"[{self}] ({devonly.func_args_values()})")
        data: memoryview = msg.get_values()[0]
        space_id, offset = kbetype.SPACE_ID.decode(data)
        data = data[offset:]

        pd = InitSpaceDataParsedData(space_id, {})
        while data:
            key, offset = kbetype.STRING.decode(data)
            data = data[offset:]
            value, offset = kbetype.STRING.decode(data)
            data = data[offset:]

            pd.pairs[key] = value

        for key, value in pd.pairs.items():
            self._space_data_mgr.set_data(pd.space_id, key, value)

        return InitSpaceDataMsgResult(success=True, result=pd)


@dataclass
class SetSpaceDataParsedData(ParsedMsgInfo):
    space_id: int = NoValue.NO_ID
    key: str = ""
    value: str = ""


@dataclass
class SetSpaceDataHandlerResult(MsgResult):
    result: SetSpaceDataParsedData
    msg_id: int = msgspec.app.client.setSpaceData.id


class SetSpaceDataHandler(SpaceDataHandler):
    def parse(self, msg: Message) -> SetSpaceDataMsgResult:
        logger.debug(f"[{self}] ({devonly.func_args_values()})")
        pd = SetSpaceDataParsedData(*msg.get_values())
        self._space_data_mgr.set_data(pd.space_id, pd.key, pd.value)
        return SetSpaceDataMsgResult(True, pd)


@dataclass
class DelSpaceDataParsedData(ParsedMsgInfo):
    space_id: int = NoValue.NO_ID
    key: str = ""


@dataclass
class DelSpaceDataHandlerResult(MsgResult):
    result: DelSpaceDataParsedData
    msg_id: int = msgspec.app.client.delSpaceData.id


class DelSpaceDataHandler(SpaceDataHandler):
    def parse(self, msg: Message) -> DelSpaceDataMsgResult:
        logger.debug(f"[{self}] ({devonly.func_args_values()})")
        pd = DelSpaceDataParsedData(*msg.get_values())
        self._space_data_mgr.del_data(pd.space_id, pd.key)
        return DelSpaceDataMsgResult(True, pd)


__all__ = [
    "SpaceDataHandler",
    "InitSpaceDataHandler",
    "SetSpaceDataHandler",
    "DelSpaceDataHandler",
]
