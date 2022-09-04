from __future__ import annotations
import asyncio
import logging
import functools
from dataclasses import dataclass
from typing import Coroutine, List, Any, Optional

from enki import dcdescr, settings
from enki.misc import devonly
from enki.interface import IClient, IMessage, IPluginCommand, IResult

logger = logging.getLogger(__name__)

TIMEOUT_ERROR_MSG = 'Timeout Error'


@dataclass
class CommandResult(IResult):
    success: bool
    result: Any = None
    text: str = ''

    _is_empty: bool = False

    @classmethod
    def get_empty(cls) -> CommandResult:
        inst = cls(False)
        inst._is_empty = True
        return inst

    @property
    def is_empty(self) -> bool:
        return self._is_empty


@dataclass
class _RequestData:
    sent_msg_spec: dcdescr.MessageDescr
    success_msg_spec: Optional[dcdescr.MessageDescr]
    error_msg_specs: List[dcdescr.MessageDescr]
    future: asyncio.Future
    timeout: float


class Command(IPluginCommand):
    """Base class for commands.

    The command is a request-response communication approach between
    the client and the server. A descendent class encapsulates request and
    response data and gives the asynchronous interface to use the "execute"
    command method like a coroutine.

    A descendent should override the "execute" method and set the response and
    request messages to the variables below.
    """
    _req_msg_spec: dcdescr.MessageDescr
    _success_resp_msg_spec: Optional[dcdescr.MessageDescr]
    _error_resp_msg_specs: list[dcdescr.MessageDescr]

    def __init__(self, client: IClient):
        self._client = client
        self._req_data_by_msg_id: dict[int, _RequestData] = {}

    def on_receive_msg(self, msg: IMessage) -> bool:
        """
        The method returns True if the command is waiting for the message.
        I.e. the message will be handled.
        """
        logger.info(f'[{self}]  ({devonly.func_args_values()})')
        req_data = self._req_data_by_msg_id.get(msg.id, None)
        if req_data is None:
            logger.debug(f'[{self}] The message "{msg.id}" is not being waited for')
            return False
        future = req_data.future
        future.set_result(msg)
        logger.debug('[%s] The message "%s" is set to the future', self, msg.id)

        return True

    def on_end_receive_msg(self):
        self._fini()

    async def execute(self) -> Any:
        raise NotImplementedError

    @functools.cached_property
    def waiting_for_ids(self) -> list[int]:
        ids = []
        if self._success_resp_msg_spec is not None:
            ids.append(self._success_resp_msg_spec.id)
        ids += [s.id for s in self._error_resp_msg_specs]
        return ids

    def get_timeout_err_text(self) -> str:
        success_msg = self._success_resp_msg_spec.name \
            if self._success_resp_msg_spec else '<not set>'
        error_msgs = ', '.join(f'"{m.name}"' for m in self._error_resp_msg_specs)
        return f'No response nor for success message "{success_msg}" ' \
               f'nor for error messages {error_msgs} ' \
               f'(sent message = "{self._req_msg_spec.name}")'

    def _waiting_for(self, timeout: float = settings.WAITING_FOR_SERVER_TIMEOUT
                     ) -> Coroutine[None, None, Optional[IMessage]]:
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
            return None

        return res

    def _fini(self):
        for msg_id, data in self._req_data_by_msg_id.items():
            logger.debug(f'[{self}] Cancel the "{msg_id}" command ...')
            data.future.cancel()
        self._req_data_by_msg_id.clear()

    def __str__(self):
        state = f'waiting for "{self.waiting_for_ids}"'
        return f'{self.__class__.__name__}({state})'
