from __future__ import annotations
import abc
import logging
from typing import List, Awaitable, Any, ClassVar

from enki import message, interface, utils

logger = logging.getLogger(__name__)


class Command(interface.IReturningCommand,
              interface.IMsgReceiver,
              interface.IMsgRespAwaitable,
              utils.MsgRespAwaitableMixIn):
    """Abstract class for commands."""

    _req_msg_spec: ClassVar[message.MessageSpec]
    _success_resp_msg_spec: ClassVar[message.MessageSpec]
    _error_resp_msg_specs: ClassVar[List[message.MessageSpec]]

    def on_receive_msg(self, msg: interface.IMessage) -> bool:
        return utils.MsgRespAwaitableMixIn.on_receive_msg(self, msg)

    async def send(self, msg: interface.IMessage) -> None:
        """Send the message."""
        return await utils.MsgRespAwaitableMixIn.send(self, msg)

    def waiting_for(self, success_msg_spec: int, error_msg_specs: List[int], timeout: int
                    ) -> Awaitable[interface.IMessage]:
        return utils.MsgRespAwaitableMixIn.waiting_for(
            self, success_msg_spec, error_msg_specs, timeout
        )

    @abc.abstractmethod
    def execute(self) -> Any:
        pass
