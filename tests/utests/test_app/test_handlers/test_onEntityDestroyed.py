import unittest

from enki.app import handlers, appl
from enki import kbeclient, descr, settings
from enki.app.managers import entitymgr
from enki.interface import IMessage, IMsgReceiver

from tests.utests import base


class OnEntityDestroyedTestCase(base.EnkiTestCaseBase):
    """Test Client::onEntityDestroyed"""

    def test_ok(self):
        self.call_OnCreatedProxies()

        data = b'\x00\x02\x81\x08\x00\x00\xff\x01 \x00\xf1\x00\x00\x00\x00\x08\x07\x00\x00\x00\xf1\x00\x00\x00\x03\x00\x00\x00\x00\t\x07\x00\x00\x00\xf1\x00\x00\x00\x03\x00\x00\x00\xf8\x01\x13\x00\x00\x00\x07\x00\xbd6\xfeb\xf1\x00\x00\x00Avatar\x00\xff\x01\xb1\x00\xf1\x00\x00\x00\x00\x03\x01\x00\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04d\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x08\x07\x00\x00\x00\xf1\x00\x00\x00\x03\x00\x02\x00\x08\x04\xe9\x03\x00\x00\x08\x05\xc8\x01\x00\x00\x00\n\x07\x00\x00\x00\xf1\x00\x00\x00\x04\x00\x02\x00\n\x04\xe9\x03\x00\x00\n\x05x\x03\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x0c\x01\x00\x00\r\x81J]\x05\x00\x0e\x01\x00\x0f<\x00\x10\x07\x00\x00\x00Damkina\x00\x11\x00\x00\x00\x12\x01\x00\x00\x00\x00\x13\x00\x00\x14\x00\x00\x15\x00\x00\x00\x00\x00\x16\x00\x00\x00\x00\xfa\x01\n\x00\xf1\x00\x00\x00\n\x01\t\x03\x00\x00\xff\x01 \x00\xf1\x00\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x01\x06\x00\xf1\x00\x00\x00\x02\x00\xff\x01\n\x00\xf1\x00\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\xf1\x00\x00\x00\x00\x07d\x00\x00\x00'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        entity_id, *_ = msg.get_values()
        self._entity_mgr.initialize_entity(entity_id, 'Account', True)
        handler = handlers.OnEntityDestroyedHandler(self._entity_mgr)
        result: handlers.HandlerResult = handler.handle(msg)
        assert result.success
        assert self._entity_mgr.get_entity(entity_id).isDestroyed

    def test_chunk_512(self):
        data = b'\x00\x02\x7f\x08\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\x00\t\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\xf8\x01\x13\x00\x00\x00\x07\x00\xdd\x10\xffb\x80\x08\x00\x00Avatar\x00\xff\x01\xb1\x00\x80\x08\x00\x00\x00\x03\x01\x00\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04d\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x02\x00\x08\x04\xe9\x03\x00\x00\x08\x05\xc8\x01\x00\x00\x00\n\x07\x00\x00\x00\x80\x08\x00\x00\x04\x00\x02\x00\n\x04\xe9\x03\x00\x00\n\x05x\x03\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x0c\x01\x00\x00\r\x81J]\x05\x00\x0e\x01\x00\x0f<\x00\x10\x07\x00\x00\x00Damkina\x00\x11\x00\x00\x00\x12\x01\x00\x00\x00\x00\x13\x00\x00\x14\x00\x00\x15\x00\x00\x00\x00\x00\x16\x00\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\n\x01\t\x03\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x01\x06\x00\x80\x08\x00\x00\x02\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x07d\x00\x00\x00\x00\x02\x7f\x08\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\x00\t\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\xf8\x01\x13\x00\x00\x00\x07\x00\xdd\x10\xffb\x80\x08\x00\x00Avatar\x00\xff\x01\xb1\x00\x80\x08\x00\x00\x00\x03\x01\x00\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04d\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x02\x00\x08\x04\xe9\x03\x00\x00\x08\x05\xc8\x01\x00\x00\x00\n\x07\x00\x00\x00\x80\x08\x00\x00\x04\x00\x02\x00\n\x04\xe9\x03\x00\x00\n\x05x\x03\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x0c\x01\x00\x00\r\x81J]\x05\x00\x0e\x01\x00\x0f<\x00\x10\x07\x00\x00\x00Damkina\x00\x11\x00\x00\x00\x12\x01\x00\x00\x00\x00\x13\x00\x00\x14\x00\x00\x15\x00\x00\x00\x00\x00\x16\x00\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\n\x01\t\x03\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x01\x06\x00\x80\x08\x00\x00\x02\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x07d\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\x08\x01o\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\x08\x01o\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\n\x01x\x03\x00\x00A\x00\x1f\x00\x01\x00\x00\x00_mapping\x00spaces/xinshoucun\x00\x0c\x00\x1c\x00\x80\x08\x00\x00\x81\xe5@D\x83\x00SC3#BD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfd\x01\t\x00\x80\x08\x00\x00\x01\x00\x00\x00\x00\x00\x02\x7f\x08\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\x00\t\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\xf8\x01\x13\x00\x00\x00\x07\x00\xdd\x10\xffb\x80\x08\x00\x00Avatar\x00\xff\x01\xb1\x00\x80\x08\x00\x00\x00\x03\x01\x00\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04d\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x02\x00\x08\x04\xe9\x03\x00\x00\x08\x05\xc8\x01\x00\x00\x00\n\x07\x00\x00\x00\x80\x08\x00\x00\x04\x00\x02\x00\n\x04\xe9\x03\x00\x00\n\x05x\x03\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x0c\x01\x00\x00\r\x81J]\x05\x00\x0e\x01\x00\x0f<\x00\x10\x07\x00\x00\x00Damkina\x00\x11\x00\x00\x00\x12\x01\x00\x00\x00\x00\x13\x00\x00\x14\x00\x00\x15\x00\x00\x00\x00\x00\x16\x00\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\n\x01\t\x03\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x01\x06\x00\x80\x08\x00\x00\x02\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x07d\x00\x00\x00\x00\x02\x7f\x08\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\x00\t\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\xf8\x01\x13\x00\x00\x00\x07\x00\xdd\x10\xffb\x80\x08\x00\x00Avatar\x00\xff\x01\xb1\x00\x80\x08\x00\x00\x00\x03\x01\x00\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04d\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x02\x00\x08\x04\xe9\x03\x00\x00\x08\x05\xc8\x01\x00\x00\x00\n\x07\x00\x00\x00\x80\x08\x00\x00\x04\x00\x02\x00\n\x04\xe9\x03\x00\x00\n\x05x\x03\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x0c\x01\x00\x00\r\x81J]\x05\x00\x0e\x01\x00\x0f<\x00\x10\x07\x00\x00\x00Damkina\x00\x11\x00\x00\x00\x12\x01\x00\x00\x00\x00\x13\x00\x00\x14\x00\x00\x15\x00\x00\x00\x00\x00\x16\x00\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\n\x01\t\x03\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x01\x06\x00\x80\x08\x00\x00\x02\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x07d\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\x08\x01o\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\x08\x01o\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\n\x01x\x03\x00\x00A\x00\x1f\x00\x01\x00\x00\x00_mapping\x00spaces/xinshoucun\x00\x0c\x00\x1c\x00\x80\x08\x00\x00\x81\xe5@D\x83\x00SC3#BD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfd\x01\t\x00\x80\x08\x00\x00\x01\x00\x00\x00\x00\r\x00\x81\xe5@D\x83\x00SC3#BD\xff\x01t\x00\x04\x00\x00\x00\x00\x01\xd1\xd6KD|2SC\xd1\xa6AD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00;\xadi?\x00\x04d\x00\x00\x00\x00\x05d\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07d\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\n\xe901\x01\x00\x0b\n\x00\x0c2\x00\r\x0c\x00\x00\x00\xe8\x89\xbe\xe5\x85\x8b\xe6\x96\xaf\xe7\x90\x83\x00\x0e\x00\x00\x0f\x00\x00\x10\xe901\x01\x00\x11\x01\x00\x00\x00\xfb\x01\x06\x00\x04\x00\x00\x00\x05\x00\xff\x01S\x00\x01\x00\x00\x00\x00\x01\x8e\x01DDM\xf3RCq\x91CD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\xa0\xc40\xc0\x00\x04\x00\x00\x00\x00\x00\x05i\x9a\x98\x00\x00\x06\x0f\x00\x072\x00\x08\x0f\x00\x00\x00\xe6\x96\xb0\xe6\x89\x8b\xe6\x8e\xa5\xe5\xbe\x85\xe5\x91\x98\x00\ti\x9a\x98\x00\x00\n\x01\x00\x00\x00\xfb\x01\x06\x00\x01\x00\x00\x00\x06\x00\x00\x02\x7f\x08\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\x00\t\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\xf8\x01\x13\x00\x00\x00\x07\x00\xdd\x10\xffb\x80\x08\x00\x00Avatar\x00\xff\x01\xb1\x00\x80\x08\x00\x00\x00\x03\x01\x00\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04d\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x02\x00\x08\x04\xe9\x03\x00\x00\x08\x05\xc8\x01\x00\x00\x00\n\x07\x00\x00\x00\x80\x08\x00\x00\x04\x00\x02\x00\n\x04\xe9\x03\x00\x00\n\x05x\x03\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x0c\x01\x00\x00\r\x81J]\x05\x00\x0e\x01\x00\x0f<\x00\x10\x07\x00\x00\x00Damkina\x00\x11\x00\x00\x00\x12\x01\x00\x00\x00\x00\x13\x00\x00\x14\x00\x00\x15\x00\x00\x00\x00\x00\x16\x00\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\n\x01\t\x03\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x01\x06\x00\x80\x08\x00\x00\x02\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x07d\x00\x00\x00\x00\x02\x7f\x08\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\x00\t\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\xf8\x01\x13\x00\x00\x00\x07\x00\xdd\x10\xffb\x80\x08\x00\x00Avatar\x00\xff\x01\xb1\x00\x80\x08\x00\x00\x00\x03\x01\x00\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04d\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x02\x00\x08\x04\xe9\x03\x00\x00\x08\x05\xc8\x01\x00\x00\x00\n\x07\x00\x00\x00\x80\x08\x00\x00\x04\x00\x02\x00\n\x04\xe9\x03\x00\x00\n\x05x\x03\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x0c\x01\x00\x00\r\x81J]\x05\x00\x0e\x01\x00\x0f<\x00\x10\x07\x00\x00\x00Damkina\x00\x11\x00\x00\x00\x12\x01\x00\x00\x00\x00\x13\x00\x00\x14\x00\x00\x15\x00\x00\x00\x00\x00\x16\x00\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\n\x01\t\x03\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x01\x06\x00\x80\x08\x00\x00\x02\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x07d\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\x08\x01o\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\x08\x01o\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\n\x01x\x03\x00\x00A\x00\x1f\x00\x01\x00\x00\x00_mapping\x00spaces/xinshoucun\x00\x0c\x00\x1c\x00\x80\x08\x00\x00\x81\xe5@D\x83\x00SC3#BD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfd\x01\t\x00\x80\x08\x00\x00\x01\x00\x00\x00\x00\x00\x02\x7f\x08\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\x00\t\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\xf8\x01\x13\x00\x00\x00\x07\x00\xdd\x10\xffb\x80\x08\x00\x00Avatar\x00\xff\x01\xb1\x00\x80\x08\x00\x00\x00\x03\x01\x00\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04d\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x02\x00\x08\x04\xe9\x03\x00\x00\x08\x05\xc8\x01\x00\x00\x00\n\x07\x00\x00\x00\x80\x08\x00\x00\x04\x00\x02\x00\n\x04\xe9\x03\x00\x00\n\x05x\x03\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x0c\x01\x00\x00\r\x81J]\x05\x00\x0e\x01\x00\x0f<\x00\x10\x07\x00\x00\x00Damkina\x00\x11\x00\x00\x00\x12\x01\x00\x00\x00\x00\x13\x00\x00\x14\x00\x00\x15\x00\x00\x00\x00\x00\x16\x00\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\n\x01\t\x03\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x01\x06\x00\x80\x08\x00\x00\x02\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x07d\x00\x00\x00\x00\x02\x7f\x08\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\x00\t\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x00\x00\xf8\x01\x13\x00\x00\x00\x07\x00\xdd\x10\xffb\x80\x08\x00\x00Avatar\x00\xff\x01\xb1\x00\x80\x08\x00\x00\x00\x03\x01\x00\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04d\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x08\x07\x00\x00\x00\x80\x08\x00\x00\x03\x00\x02\x00\x08\x04\xe9\x03\x00\x00\x08\x05\xc8\x01\x00\x00\x00\n\x07\x00\x00\x00\x80\x08\x00\x00\x04\x00\x02\x00\n\x04\xe9\x03\x00\x00\n\x05x\x03\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x0c\x01\x00\x00\r\x81J]\x05\x00\x0e\x01\x00\x0f<\x00\x10\x07\x00\x00\x00Damkina\x00\x11\x00\x00\x00\x12\x01\x00\x00\x00\x00\x13\x00\x00\x14\x00\x00\x15\x00\x00\x00\x00\x00\x16\x00\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\n\x01\t\x03\x00\x00\xff\x01 \x00\x80\x08\x00\x00\x00\x01\x81\xe5@D\x83\x00SC3#BD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x01\x06\x00\x80\x08\x00\x00\x02\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x05d\x00\x00\x00\xff\x01\n\x00\x80\x08\x00\x00\x00\x07d\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\x08\x01o\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\x08\x01o\x00\x00\x00\xfa\x01\n\x00\x80\x08\x00\x00\n\x01x\x03\x00\x00A\x00\x1f\x00\x01\x00\x00\x00_mapping\x00spaces/xinshoucun\x00\x0c\x00\x1c\x00\x80\x08\x00\x00\x81\xe5@D\x83\x00SC3#BD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfd\x01\t\x00\x80\x08\x00\x00\x01\x00\x00\x00\x00\r\x00\x81\xe5@D\x83\x00SC3#BD\xff\x01t\x00\x04\x00\x00\x00\x00\x01\xd1\xd6KD|2SC\xd1\xa6AD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00;\xadi?\x00\x04d\x00\x00\x00\x00\x05d\x00\x00\x00\x00\x06d\x00\x00\x00\x00\x07d\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\n\xe901\x01\x00\x0b\n\x00\x0c2\x00\r\x0c\x00\x00\x00\xe8\x89\xbe\xe5\x85\x8b\xe6\x96\xaf\xe7\x90\x83\x00\x0e\x00\x00\x0f\x00\x00\x10\xe901\x01\x00\x11\x01\x00\x00\x00\xfb\x01\x06\x00\x04\x00\x00\x00\x05\x00\xff\x01S\x00\x01\x00\x00\x00\x00\x01\x8e\x01DDM\xf3RCq\x91CD\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\xa0\xc40\xc0\x00\x04\x00\x00\x00\x00\x00\x05i\x9a\x98\x00\x00\x06\x0f\x00\x072\x00\x08\x0f\x00\x00\x00\xe6\x96\xb0\xe6\x89\x8b\xe6\x8e\xa5\xe5\xbe\x85\xe5\x91\x98\x00\ti\x9a\x98\x00\x00\n\x01\x00\x00\x00\xfb\x01\x06\x00\x01\x00\x00\x00\x06\x00\x1d\x00\r\x00\x00B\xc6KD3\xc2AD\xf4<\x0b\xbf\x1d\x00\r\x00\x00\xb3\xb5KD\x95\xddAD\xf4<\x0b\xbf'
        msg, data_tail = kbeclient.Serializer().deserialize(memoryview(data))
        assert msg is not None, 'Invalid initial data'

        entity_id, *_ = msg.get_values()
        self._entity_mgr.initialize_entity(entity_id, 'Account', True)
        handler = handlers.OnEntityDestroyedHandler(self._entity_mgr)
        result: handlers.HandlerResult = handler.handle(msg)
        assert result.success
        assert self._entity_mgr.get_entity(entity_id).isDestroyed