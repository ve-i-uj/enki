"""Integration tests for "forwardEntityMessageToCellappFromClient"."""

import asyncio
import io
import time

import enki
from enki import kbeenum, KBEngine, settings
from enki.net.command.baseapp import ForwardEntityMessageToCellappFromClientCommand
from enki.net.kbeclient import kbetype, Message, MsgDescr

from tests.itests.base import IBaseAppThreadedTestCase
from tests.data import descr

class ForwardEntityMessageToCellappFromClientCommandTestCase(IBaseAppThreadedTestCase):
    # TODO: [2023-01-16 21:46 burov_alexey@mail.ru]:
    # На данный момент тест условно рабочий. Т.к. на сервере следующая ошибка
    # forwardEntityMessageToCellappFromClienthandler::handle: Illegal access to entityID:235! proxyID=237
    # PacketReader::processMessages(Entity::forwardEntityMessageToCellappFromClient): rpos(8) invalid, expect=28. msgID=58, msglen=24.

    def test_ok(self):
        KBEngine.login('1', '1')
        enki.sync_layers(settings.SECOND * 2)

        self.call_selectAvatarGame()
        player = KBEngine.player()
        assert player is not None

        # The "useTargetSkill" method
        io_obj = io.BytesIO()
        io_obj.write(kbetype.ENTITY_ID.encode(player.id))
        io_obj.write(kbetype.UINT16.encode(0))
        io_obj.write(kbetype.ENTITY_METHOD_UID.encode(11001))

        io_obj.write(descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(1))
        io_obj.write(descr.deftype.ENTITY_FORBIDS_SPEC.kbetype.encode(1))

        # The ids of the CellApp messages:
            # Entity::onRemoteMethodCall = 302
            # Entity::onLoseWitness = 44
            # Entity::onGetWitnessFromBase = 43
            # Entity::setPosition_XYZ_float = 42
            # Entity::setPosition_XZ_float = 41
            # Entity::setPosition_XYZ_int = 40
            # Entity::setPosition_XZ_int = 39

        msg_descr = MsgDescr(
            id=302,
            lenght=-1,
            name='Cellapp::onRemoteMethodCall',
            args_type=kbeenum.MsgArgsType.VARIABLE,
            field_types=(kbetype.UINT8_ARRAY, ),
            desc=''
        )
        msgs = [
            Message(msg_descr, (io_obj.getbuffer().tobytes(), ))
        ]
        cmd = ForwardEntityMessageToCellappFromClientCommand(
            self.app.client, player.id, msgs
        )
        asyncio.run_coroutine_threadsafe(self.app.send_command(cmd), self.loop)
        enki.sync_layers(settings.SECOND * 2)
