from __future__ import annotations
import asyncio
import logging
import functools
from dataclasses import dataclass
from typing import Coroutine, List, Awaitable, Any, ClassVar, Optional

from enki import descr, dcdescr
from enki.misc import devonly
from enki.interface import IClient, IMsgReceiver, IMessage, ICommand

logger = logging.getLogger(__name__)

TIMEOUT_ERROR_MSG = 'Timeout Error'


@dataclass
class _AwaitableData:
    success_msg_spec: Optional[dcdescr.MessageDescr]
    error_msg_specs: List[dcdescr.MessageDescr]
    future: asyncio.Future


class Command(ICommand, IMsgReceiver):
    """Base class for commands.

    The command is a request-response communication approach between
    the client and the server.
    """
    _req_msg_spec: dcdescr.MessageDescr
    _success_resp_msg_spec: Optional[dcdescr.MessageDescr]
    _error_resp_msg_specs: list[dcdescr.MessageDescr]

    def __init__(self, client: IClient):
        # The client will send a response to the specified receiver
        self._client = client
        self._one_shot_msgs: dict[int, _AwaitableData] = {}

    @functools.cached_property
    def waited_ids(self) -> list[int]:
        return [self._success_resp_msg_spec.id] + \
               [s.id for s in self._error_resp_msg_specs]

    def on_receive_msg(self, msg: IMessage) -> bool:
        """
        The method returns True if the command is waiting for the message.
        I.e. the message will be handled.
        """
        logger.debug(f'[{self}]  ({devonly.func_args_values()})')
        awaitable_data = self._one_shot_msgs.get(msg.id, None)
        if awaitable_data is None:
            logger.debug(f'[{self}] The message "{msg.id}" is not being waited for')
            return False
        self._clean_one_shot_msgs(awaitable_data)
        future = awaitable_data.future
        future.set_result(msg)

        return True

    def on_end_receive_msg(self):
        for msg_id, data in self._one_shot_msgs.items():
            logger.debug(f'[{self}] Cancel the "{msg_id}" command ...')
            data.future.cancel()

    async def execute(self) -> Any:
        raise NotImplementedError

    def _waiting_for(self, success_msg_spec: dcdescr.MessageDescr,
                     error_msg_specs: List[dcdescr.MessageDescr],
                     timeout: float
                     ) -> Coroutine:
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

    async def _future_with_timeout(self, awaitable_data: _AwaitableData, timeout: float
                                   ) -> Optional[Awaitable]:
        """Coroutine wrapping timeout to future."""
        try:
            res = await asyncio.wait_for(awaitable_data.future, timeout=timeout)
        except asyncio.TimeoutError:
            self._clean_one_shot_msgs(awaitable_data)
            success_msg = awaitable_data.success_msg_spec.name
            error_msgs = ', '.join(f'"{m.name}"' for m in awaitable_data.error_msg_specs)
            msg = f'No response nor for success message "{success_msg}" ' \
                  f'nor for error messages {error_msgs}'
            logger.error(msg)
            return None

        return res

    def _clean_one_shot_msgs(self, awaitable_data: _AwaitableData):
        """Clean up warning for one shot futures."""
        self._one_shot_msgs.pop(awaitable_data.success_msg_spec.id)
        for error_msg_spec in awaitable_data.error_msg_specs:
            self._one_shot_msgs.pop(error_msg_spec.id)

    def __str__(self):
        return f'{self.__class__.__name__}(waiting for ' \
               f'"{self.waited_ids}" message(s))'
