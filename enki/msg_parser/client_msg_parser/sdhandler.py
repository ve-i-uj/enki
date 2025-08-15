"""Entity message handlers."""

import logging
from dataclasses import dataclass

from enki.app.client.layer import ilayer
from enki.app.client.layer.thlayer import IGameLayer
from enki.core import kbetype, msgspec
from enki.core.message import Message
from enki.core.novalue import NoValue
from enki.handlers.base import MsgResult, ParsedMsgInfo
from enki.misc import devonly

logger = logging.getLogger(__name__)


class SpaceDataMgr:
    @property
    def _game_layer(self) -> IGameLayer:
        return ilayer.get_game_layer()

    def set_data(self, space_id: int, key: str, value: str) -> None:
        self._game_layer.call_set_space_data(space_id, key, value)

    def del_data(self, space_id: int, key: str) -> None:
        self._game_layer.call_delete_space_data(space_id, key)


class SpaceDataMsgParser(IMsgParser):
    def __init__(self, space_data_mgr: SpaceDataMgr) -> None:
        self._space_data_mgr = space_data_mgr

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"


@dataclass
class InitSpaceDataParsedMsgData(ParsedMsgInfo):
    space_id: int
    pairs: dict[str, str]


@dataclass
class InitSpaceDataMsgParserResult(MsgResult):
    msg_id: int = msgspec.client.initSpaceData.id
    result: InitSpaceDataParsedMsgData


class InitSpaceDataHandler(SpaceDataHandler):
    def parse(self, msg: Message) -> InitSpaceDataMsgParserResult:
        logger.debug("[%s] (%s)", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        space_id, offset = kbetype.SPACE_ID.decode(data)
        data = data[offset:]

        pd = InitSpaceDataParsedMsgData(space_id, {})
        while data:
            key, offset = kbetype.STRING.decode(data)
            data = data[offset:]
            value, offset = kbetype.STRING.decode(data)
            data = data[offset:]

            pd.pairs[key] = value

        for key, value in pd.pairs.items():
            self._space_data_mgr.set_data(pd.space_id, key, value)

        return InitSpaceDataMsgParserResult(success=True, result=pd)


@dataclass
class SetSpaceDataParsedMsgData(ParsedMsgInfo):
    space_id: int = NoValue.NO_ID
    key: str = ""
    value: str = ""


@dataclass
class SetSpaceDataMsgParserResult(MsgResult):
    result: SetSpaceDataParsedMsgData
    msg_id: int = msgspec.client.setSpaceData.id


class SetSpaceDataHandler(SpaceDataHandler):
    def parse(self, msg: Message) -> SetSpaceDataMsgParserResult:
        logger.debug("[%s] (%s)", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = SetSpaceDataParsedMsgData(*values)
        self._space_data_mgr.set_data(pd.space_id, pd.key, pd.value)
        return SetSpaceDataMsgParserResult(True, pd)


@dataclass
class DelSpaceDataParsedMsgData(ParsedMsgInfo):
    space_id: int = NoValue.NO_ID
    key: str = ""


@dataclass
class DelSpaceDataMsgParserResult(MsgResult):
    result: DelSpaceDataParsedMsgData
    msg_id: int = msgspec.client.delSpaceData.id


class DelSpaceDataHandler(SpaceDataHandler):
    def parse(self, msg: Message) -> DelSpaceDataMsgParserResult:
        logger.debug("[%s] (%s)", self, devonly.func_args_values())
        values: tuple[Any, ...] = msg.get_values()
        pd = DelSpaceDataParsedMsgData(*values)
        self._space_data_mgr.del_data(pd.space_id, pd.key)
        return DelSpaceDataMsgParserResult(True, pd)


__all__ = [
    "DelSpaceDataHandler",
    "InitSpaceDataHandler",
    "SetSpaceDataHandler",
    "SpaceDataHandler",
]
