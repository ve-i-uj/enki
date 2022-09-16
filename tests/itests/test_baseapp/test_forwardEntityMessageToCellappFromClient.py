"""Integration tests for "forwardEntityMessageToCellappFromClient"."""

import asyncio
import io
from enki import msgspec, kbetype, kbeenum
from enki import dcdescr
from enki.command.baseapp import ForwardEntityMessageToCellappFromClientCommand
from enki.dcdescr import MessageDescr
from enki.interface import IMessage
from enki.kbeclient.message import Message

from tests.itests.base import IntegrationBaseAppBaseTestCase
from tests.data import demo_descr

class ForwardEntityMessageToCellappFromClientCommandTestCase(IntegrationBaseAppBaseTestCase):

    async def test_ok(self):
        await self.call_selectAvatarGame()
        player = self.app._entity_mgr.get_player()

        # The "useTargetSkill" method
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(player.id))
        io_obj.write(kbetype.UINT16.encode(0))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(11001))

        io_obj.write(demo_descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(1))
        io_obj.write(demo_descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(1))

        # The ids of the CellApp messages:
            # Entity::onRemoteMethodCall = 302
            # Entity::onLoseWitness = 44
            # Entity::onGetWitnessFromBase = 43
            # Entity::setPosition_XYZ_float = 42
            # Entity::setPosition_XZ_float = 41
            # Entity::setPosition_XYZ_int = 40
            # Entity::setPosition_XZ_int = 39

        msg_descr = MessageDescr(
            id=302,
            lenght=-1,
            name='Cellapp::onRemoteMethodCall',
            args_type=kbeenum.MsgArgsType.VARIABLE,
            field_types=(kbetype.UINT8_ARRAY, ),
            desc=''
        )
        msgs: list[IMessage] = [
            Message(msg_descr, (io_obj.getbuffer().tobytes(), ))
        ]
        handler = ForwardEntityMessageToCellappFromClientCommand(
            self.app.client, player.id, msgs
        )
        res = await handler.execute()
        assert res
