*




class TestOnEntityEnterSpace:
    """Test Client::onEntityEnterSpace."""

    def test_ok(self):
        # Avatar id is 2199
        data = b"\xf8\x01\x13\x00\x00\x00\x07\x00\xf98\xfeb\x97\x08\x00\x00Avatar\x00"
        msg_504, _ = MessageEncoder(msgspec.client.SPEC_BY_ID).deserialize(
            memoryview(data)
        )
        assert msg_504 is not None
        assert (
            OnCreatedProxiesHandler(self._entity_helper).handle(msg_504).success
        )

        data = b"\xfd\x01\t\x00\x97\x08\x00\x00\x01\x00\x00\x00\x00"
        msg, _data_tail = MessageEncoder(msgspec.client.SPEC_BY_ID).deserialize(
            memoryview(data)
        )
        assert msg is not None, "Invalid initial data"

        handler = OnEntityEnterSpaceHandler(self._entity_helper)
        result = handler.handle(msg)
        assert result.success
        assert result.result.entity_id == 2199
        assert result.result.space_id == 1
        assert not result.result.is_on_ground
