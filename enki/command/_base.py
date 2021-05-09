from __future__ import annotations
import abc
import asyncio
import logging
from dataclasses import dataclass
from typing import List, Awaitable, Any, ClassVar

from enki import descr, interface
from enki.misc import devonly

logger = logging.getLogger(__name__)


@dataclass
class _AwaitableData:
    success_msg_spec: descr.MessageSpec
    error_msg_specs: List[descr.MessageSpec]
    future: asyncio.Future


class Command(interface.IMsgReceiver):
    """Base class for commands."""

    _req_msg_spec: ClassVar[descr.MessageSpec]
    _success_resp_msg_spec: ClassVar[descr.MessageSpec]
    _error_resp_msg_specs: ClassVar[List[descr.MessageSpec]]

    def __init__(self, client: interface.IClient):
        self._client = client
        self._one_shot_msgs = {}  # type: Dict[id, _AwaitableData]

        self._client.set_msg_receiver(self)

    async def send(self, msg: interface.IMessage):
        """Send the message."""
        await self._client.send(msg)

    def waiting_for(self, success_msg_spec: descr.MessageSpec,
                    error_msg_specs: List[descr.MessageSpec],
                    timeout: int
                    ) -> Awaitable[interface.IMessage]:
        """Waiting for a response on the sent message."""
        logger.debug(f'[{self}]  ({devonly.func_args_values()})')
        future = asyncio.get_event_loop().create_future()
        awaitable_data = _AwaitableData(
            success_msg_spec=success_msg_spec,
            error_msg_specs=error_msg_specs,
            future=future
        )
        self._one_shot_msgs[success_msg_spec.id] = awaitable_data
        for error_msg_spec in error_msg_specs:
            self._one_shot_msgs[error_msg_spec.id] = awaitable_data

        coro = self._future_with_timeout(awaitable_data, timeout)
        return coro

    def on_receive_msg(self, msg: interface.IMessage) -> bool:
        logger.debug(f'[{self}]  ({devonly.func_args_values()})')
        awaitable_data = self._one_shot_msgs.get(msg.id, None)
        if awaitable_data is None:
            logger.debug(f'[{self}] The message "{msg.id}" is not being waited for')
            return False
        self._clean_one_shot_msgs(awaitable_data)
        future = awaitable_data.future
        future.set_result(msg)

        return True

    async def _future_with_timeout(self, awaitable_data: _AwaitableData, timeout: int
                                   ) -> Awaitable:
        """Coroutine wrapping timeout to future."""
        try:
            res = await asyncio.wait_for(awaitable_data.future, timeout=timeout)
        except asyncio.TimeoutError:
            self._clean_one_shot_msgs(awaitable_data)
            success_msg = awaitable_data.success_msg_spec.name
            error_msgs = ', '.join(f'"{m.name}"' for m in awaitable_data.error_msg_specs)
            msg = f'No response nor for success message "{success_msg}"' \
                  f'nor for error messages {error_msgs}'
            logger.error(msg)
            return None

        return res

    def _clean_one_shot_msgs(self, awaitable_data: _AwaitableData):
        """Clean up warning for one shot futures."""
        self._one_shot_msgs.pop(awaitable_data.success_msg_spec.id)
        for error_msg_spec in awaitable_data.error_msg_specs:
            self._one_shot_msgs.pop(error_msg_spec.id)

    def execute(self) -> Any:
        pass
