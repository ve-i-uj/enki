from __future__ import annotations
import asyncio
import logging
import functools
from dataclasses import dataclass
from typing import Coroutine, List, Awaitable, Any, ClassVar, Optional

from enki import descr, dcdescr
from enki.misc import devonly
from enki.interface import IClient, IMsgReceiver, IMessage, ICommand, IResult

logger = logging.getLogger(__name__)

TIMEOUT_ERROR_MSG = 'Timeout Error'


@dataclass
class CommandResult(IResult):
    success: bool
    text: str = ''


@dataclass
class _RequestData:
    sent_msg_spec: dcdescr.MessageDescr
    success_msg_spec: Optional[dcdescr.MessageDescr]
    error_msg_specs: List[dcdescr.MessageDescr]
    future: asyncio.Future
    timeout: float


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
        self._req_data_by_msg_id: dict[int, _RequestData] = {}

    @functools.cached_property
    def waited_ids(self) -> list[int]:
        ids = []
        if self._success_resp_msg_spec is not None:
            ids.append(self._success_resp_msg_spec.id)
        ids += [s.id for s in self._error_resp_msg_specs]
        return ids

    def on_receive_msg(self, msg: IMessage) -> bool:
        """
        The method returns True if the command is waiting for the message.
        I.e. the message will be handled.
        """
        logger.debug(f'[{self}]  ({devonly.func_args_values()})')
        req_data = self._req_data_by_msg_id.get(msg.id, None)
        if req_data is None:
            logger.debug(f'[{self}] The message "{msg.id}" is not being waited for')
            return False
        future = req_data.future
        future.set_result(msg)

        return True

    def on_end_receive_msg(self):
        for msg_id, data in self._req_data_by_msg_id.items():
            logger.debug(f'[{self}] Cancel the "{msg_id}" command ...')
            data.future.cancel()

    async def execute(self) -> Any:
        raise NotImplementedError

    def _waiting_for(self, timeout: float) -> Coroutine[None, None, Optional[IMessage]]:
        """Waiting for a response on the sent message."""
        logger.debug(f'[{self}]  ({devonly.func_args_values()})')
        future = asyncio.get_event_loop().create_future()
        awaitable_data = _RequestData(
            sent_msg_spec=self._req_msg_spec,
            success_msg_spec=self._success_resp_msg_spec,
            error_msg_specs=self._error_resp_msg_specs,
            future=future,
            timeout=timeout
        )
        if self._success_resp_msg_spec is not None:
            self._req_data_by_msg_id[self._success_resp_msg_spec.id] = awaitable_data
        for error_msg_spec in self._error_resp_msg_specs:
            self._req_data_by_msg_id[error_msg_spec.id] = awaitable_data

        coro = self._future_with_timeout(awaitable_data)
        return coro

    async def _future_with_timeout(self, req_data: _RequestData) -> Any:
        """Coroutine wrapping timeout to future."""
        try:
            res = await asyncio.wait_for(req_data.future, req_data.timeout)
        except asyncio.TimeoutError:
            success_msg = req_data.success_msg_spec.name \
                if req_data.success_msg_spec else '<not set>'
            error_msgs = ', '.join(f'"{m.name}"' for m in req_data.error_msg_specs)
            msg = f'No response nor for success message "{success_msg}" ' \
                f'nor for error messages {error_msgs} ' \
                f'(sent message = "{req_data.sent_msg_spec.name}")'
            if req_data.success_msg_spec is None:
                logger.debug(msg)
            else:
                logger.warning(msg)
            return None

        return res

    def __str__(self):
        return f'{self.__class__.__name__}(waiting for ' \
               f'"{self.waited_ids}" message(s))'
