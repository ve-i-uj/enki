import pytest


class TestOnUpdateBasePosXZ:
    """Test onUpdateBaseXZPos."""

    @pytest.mark.skip("Not implemented yet")
    def test_ok(self):
        self.call_OnCreatedProxies()

        data = b"\x0f\x00\x81\xe5@D3#BD"
        msg, _data_tail = MessageEncoder(msgspec.client.SPEC_BY_ID).deserialize(
            memoryview(data)
        )
        assert msg is not None, "Invalid initial data"

        handler = OnUpdateBasePosXZHandler(self._entity_helper)
        result = handler.handle(msg)
        assert result.success
        assert result.result.x == 771.5859985351562
        assert result.result.z == 776.5499877929688
