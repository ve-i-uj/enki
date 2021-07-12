"""Entity message handlers."""

import logging
from dataclasses import dataclass
from typing import Dict, Any

from enki import descr, kbetype, kbeenum, kbeclient
from enki.misc import devonly

from . import base

logger = logging.getLogger(__name__)


@dataclass
class OnUpdatePropertysParsedData(base.ParsedMsgData):
    entity_id: int
    properties: Dict[str, Any]


@dataclass
class OnUpdatePropertysHandlerResult(base.HandlerResult):
    success: OnUpdatePropertysParsedData
    msg_id: int = descr.app.client.onUpdatePropertys.id
    msg_route: base.MsgRoute = base.MsgRoute.ENTITY


class OnUpdatePropertysHandler(base.IHandler):

    def handle(self, msg: kbeclient.Message) -> OnUpdatePropertysHandlerResult:
        """Handler of `onUpdatePropertys`."""
        logger.debug(f'[{self}] ({devonly.func_args_values()})')
        entity_id, data = msg.get_values()

        result = OnUpdatePropertysParsedData(
            entity_id=entity_id,
            properties={}
        )
        # TODO: [03.07.2021 burov_alexey@mail.ru]:
        # Искать нужно не по id сущности, а по id класса сущности
        entity_desc = descr.entity.DESC_BY_UID[entity_id]
        while data:
            uid, shift = kbetype.UINT16.decode(data)
            data = data[shift:]
            child_uid, shift = kbetype.UINT16.decode(data)
            data = data[shift:]

            if uid == 0 and child_uid in kbeenum.PropertyUType.__members__:
                # It's dimension data
                child_uid = kbeenum.PropertyUType(child_uid)
                if child_uid == kbeenum.PropertyUType.POSITION_XYZ:
                    raise
                elif child_uid == kbeenum.PropertyUType.DIRECTION_ROLL_PITCH_YAW:
                    raise
                elif child_uid == kbeenum.PropertyUType.SPACE_ID:
                    space_id, shift = kbetype.SPACE_ID.decode(data)
                    data = data[shift:]
                    result.properties['space_id'] = space_id
                    continue

            # we're going to decode other properties here
            type_spec = descr.entity.DESC_BY_UID[child_uid]
            value, shift = type_spec.kbetype.decode(data)
            data = data[shift:]
            property_id, shift = kbetype.UINT16.decode(data)
            data = data[shift:]
            # descr.deftype.TYPE_BY_ID[]

        return OnUpdatePropertysHandlerResult(result=result)
