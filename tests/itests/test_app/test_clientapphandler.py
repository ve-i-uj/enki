
import asyncio
import unittest
from unittest.mock import MagicMock
from enki.app.client import appl

from enki.core import msgspec
from enki.net.addr import Addr
from enki.net.client import MessageEncoder
from enki.app import client
from enki.app.client.clienthandler.ehelper import EntityHelper
from enki.app.client.layer import ilayer
from enki.app.client.appl import OnCreatedProxiesClientAppHandler, \
    OnEntityEnterWorldClientAppHandler, OnUpdatePropertysClientAppHandler

from tests.utests.base import EnkiBaseTestCase

from tests.data import descr, entities


class OnCreatedProxiesTestCase(EnkiBaseTestCase):
    """Test onCreatedProxies"""

    async def test_on_update_and_on_created_proxy(self):
        """Ещё до создания сущности приходит сообщение об обновлении свойств.

        Это сообщение нужно сохранить.
        """
        client.start(
            Addr('localhost', 20013),
            descr.description.DESC_BY_UID,
            descr.eserializer.SERIAZER_BY_ECLS_NAME,
            descr.kbenginexml.root(),
            entities.ENTITY_CLS_BY_NAME
        )
        app = client._app
        # Имитируем, что приложение подключено
        app._state = appl._AppStateEnum.CONNECTED
        # Подменим слои на моки
        ilayer.init(MagicMock(), MagicMock())

        data = b'\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        # onUpdatePropertys
        msg_511, data_tail = MessageEncoder(msgspec.client.SPEC_BY_ID).deserialize(memoryview(data))
        assert msg_511 is not None, 'Invalid initial data'

        # Сообщение об обновлении пришло до создания сущности. Оно должно
        # быть сохранено и переотправлено, когда сущность будет создана.
        assert not app._pending_msgs_by_entity_id
        app.on_receive_msg(msg_511)
        # Уснём на секунду, чтобы поймать таск в следующем тике
        await asyncio.sleep(1)
        assert len(app._pending_msgs_by_entity_id) == 1
        # 243 - это id сущности
        assert msgspec.client.onUpdatePropertys.id == app._pending_msgs_by_entity_id[243][0].id
        # В игру уведомления не было
        assert ilayer.get_game_layer().call_entity_created.call_count == 0
        assert ilayer.get_game_layer().update_entity_properties.call_count == 0

        # Теперь пришлои onCreatedProxies. Сообщения 511 должны быть пересланы
        data = b'\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00'
        msg_504, data_tail = MessageEncoder(msgspec.client.SPEC_BY_ID).deserialize(memoryview(data))
        assert msg_504 is not None, 'Invalid initial data'
        app.on_receive_msg(msg_504)
        await asyncio.sleep(1)
        assert not app._pending_msgs_by_entity_id
        assert ilayer.get_game_layer().call_entity_created.call_count == 1
        assert ilayer.get_game_layer().update_entity_properties.call_count == 1
