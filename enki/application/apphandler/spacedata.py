"""Entity message handlers."""

import logging
from dataclasses import dataclass
from typing import Dict, Optional

from enki import descr, kbetype, kbeclient
from enki.misc import devonly

from enki.application.apphandler import base

logger = logging.getLogger(__name__)


class SpaceDataHandler(base.IHandler):

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


@dataclass
class InitSpaceDataParsedData(base.ParsedMsgData):
    space_id: int
    pairs: Dict[str, str]


@dataclass
class InitSpaceDataHandlerResult(base.HandlerResult):
    success: bool
    msg_id: int = descr.app.client.initSpaceData.id
    result: InitSpaceDataParsedData
    text: Optional[str] = None


class InitSpaceDataHandler(SpaceDataHandler):

    def handle(self, msg: kbeclient.Message) -> InitSpaceDataHandlerResult:
        """Handler of `onUpdatePropertys`."""
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

        return InitSpaceDataHandlerResult(
            success=True,
            result=pd
        )
