"""Entity message handlers."""

import logging
from dataclasses import dataclass
from typing import Dict, Any

from enki import message, kbetype, kbeenum
from enki.misc import devonly

from . import base

logger = logging.getLogger(__name__)


@dataclass
class OnUpdatePropertysParsedData(base.ParsedMsgData):
    entity_id: int
    properties: Dict[str, Any]


@dataclass
class OnUpdatePropertysHandlerResult(base.HandlerResult):
    result: OnUpdatePropertysParsedData
    msg_id: int = message.app.client.onUpdatePropertys.id
    msg_route: base.MsgRoute = base.MsgRoute.ENTITY


class OnUpdatePropertysHandler(base.IHandler):

    def handle(self, msg: message.Message) -> OnUpdatePropertysHandlerResult:
        """Handler of `onUpdatePropertys`."""
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        entity_id, data = msg.get_values()
        uid, shift = kbetype.UINT16.decode(data)
        data = data[shift:]
        child_uid, shift = kbetype.UINT16.decode(data)
        data = data[shift:]

        result = OnUpdatePropertysParsedData(
            entity_id=entity_id,
            properties={}
        )

        if uid == 0:
            # It's dimension data
            child_uid = kbeenum.PropertyUType(child_uid)
            if child_uid == kbeenum.PropertyUType.POSITION_XYZ:
                raise
            elif child_uid == kbeenum.PropertyUType.DIRECTION_ROLL_PITCH_YAW:
                raise
            if child_uid == kbeenum.PropertyUType.SPACE_ID:
                space_id, shift = kbetype.SPACE_ID.decode(data)
                data = data[shift:]

        result.properties['space_id'] = space_id

        # Now we're going to get other properties
        while data:
            delimiter, shift = kbetype.UINT16.decode(data)
            assert delimiter == 0
            data = data[shift:]
            property_id, shift = kbetype.UINT16.decode(data)
            data = data[shift:]
            message.deftype.TYPE_BY_ID[]

        return OnUpdatePropertysHandlerResult(result=result)
