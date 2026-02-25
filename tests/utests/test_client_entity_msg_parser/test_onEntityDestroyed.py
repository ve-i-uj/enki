import pytest

from tests.utests import conftest


class TestOnEntityDestroyed:
    """Test Client::onEntityDestroyed."""

    @pytest.mark.skip("Not implemented yet")
    def test_ok(self):
        """Сперва нужно сущность создать потом только уничтожить."""
        self.call_OnCreatedProxies()

        data = b"\x00\x02\x81\x08\x00\x00"
        msg, _data_tail = MessageEncoder(msgspec.client.SPEC_BY_ID).deserialize(
            memoryview(data)
        )
        assert msg is not None, "Invalid initial data"

        handler = OnEntityDestroyedHandler(self._entity_helper)
        result = handler.handle(msg)
        assert result.success
