from unittest import IsolatedAsyncioTestCase

from enki import msgspec
from enki.command.common import RequestCommand
from enki.handlers.server_handlers.common import OnLookAppParsedMsgData
from enki.kbeenum import ComponentType
from enki.msg.message import Message
from enki.net.addr import Addr


class QueryLoadCommandTestCase(IsolatedAsyncioTestCase):
    async def test_ok(self):
        cmd_lookApp = RequestCommand(
            Addr("localhost", 20099),
            Message(msgspec.machine.lookApp, ()),
            msgspec.custom.onLookApp.change_component_owner(
                ComponentType.MACHINE
            ),
            stop_on_first_data_chunk=True,
        )
        res = await cmd_lookApp.execute()
        assert res.success

        msgs = res.result
        msg = msgs[0]
        values: tuple[Any, ...] = msg.get_values()
        pd = OnLookAppParsedMsgData(*values)
        assert pd.component_type == ComponentType.MACHINE
