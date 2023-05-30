import asynctest
from enki.command.common import RequestCommand

from enki.core import msgspec
from enki.core.kbeenum import ComponentType
from enki.core.message import Message
from enki.core.enkitype import AppAddr
from enki.handler.serverhandler.common import OnLookAppParsedData


class QueryLoadCommandTestCase(asynctest.TestCase):

    async def test_ok(self):
        cmd_lookApp = RequestCommand(
            AppAddr('localhost', 20099),
            Message(msgspec.app.machine.lookApp, tuple()),
            msgspec.custom.onLookApp.change_component_owner(ComponentType.MACHINE),
            stop_on_first_data_chunk=True
        )
        res = await cmd_lookApp.execute()
        assert res.success

        msgs = res.result
        msg = msgs[0]
        pd = OnLookAppParsedData(*msg.get_values())
        assert pd.component_type == ComponentType.MACHINE
