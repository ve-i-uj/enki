"""Entity message handlers."""

import collections
import logging
from dataclasses import dataclass
from typing import Dict, Optional

from enki import settings
from enki.net import msgspec, kbeclient
from enki import devonly

from enki.app.handler import base

from enki.net.kbeclient import kbetype

logger = logging.getLogger(__name__)


class SpaceDataMgr:

    def __init__(self) -> None:
        self._data: dict[int, dict[str, str]] = collections.defaultdict(dict)

    def get_data(self, space_id: int, key: str) -> str:
        return self._data[space_id][key]

    def set_data(self, space_id: int, key: str, value: str):
        self._data[space_id][key] = value

    def del_data(self, space_id: int, key: str):
        del self._data[space_id][key]


class SpaceDataHandler(base.Handler):

    def __init__(self, space_data_mgr: SpaceDataMgr) -> None:
        self._space_data_mgr = space_data_mgr

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


@dataclass
class InitSpaceDataParsedData(base.ParsedMsgData):
    space_id: int
    pairs: Dict[str, str]


@dataclass
class InitSpaceDataHandlerResult(base.HandlerResult):
    msg_id: int = msgspec.app.client.initSpaceData.id
    result: InitSpaceDataParsedData


class InitSpaceDataHandler(SpaceDataHandler):

    def handle(self, msg: kbeclient.Message) -> InitSpaceDataHandlerResult:
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
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

        return InitSpaceDataHandlerResult(
            success=True,
            result=pd
        )


@dataclass
class SetSpaceDataParsedData(base.ParsedMsgData):
    space_id: int = settings.NO_ID
    key: str = ''
    value: str = ''


@dataclass
class SetSpaceDataHandlerResult(base.HandlerResult):
    result: SetSpaceDataParsedData
    msg_id: int = msgspec.app.client.setSpaceData.id


class SetSpaceDataHandler(SpaceDataHandler):

    def handle(self, msg: kbeclient.Message) -> SetSpaceDataHandlerResult:
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        pd = SetSpaceDataParsedData(*msg.get_values())
        self._space_data_mgr.set_data(pd.space_id, pd.key, pd.value)
        return SetSpaceDataHandlerResult(True, pd)


@dataclass
class DelSpaceDataParsedData(base.ParsedMsgData):
    space_id: int = settings.NO_ID
    key: str = ''


@dataclass
class DelSpaceDataHandlerResult(base.HandlerResult):
    result: DelSpaceDataParsedData
    msg_id: int = msgspec.app.client.delSpaceData.id


class DelSpaceDataHandler(SpaceDataHandler):

    def handle(self, msg: kbeclient.Message) -> DelSpaceDataHandlerResult:
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        pd = DelSpaceDataParsedData(*msg.get_values())
        self._space_data_mgr.del_data(pd.space_id, pd.key)
        return DelSpaceDataHandlerResult(True, pd)


__all__ = [
    'SpaceDataHandler',
    'InitSpaceDataHandler',
    'SetSpaceDataHandler',
    'DelSpaceDataHandler'
]
