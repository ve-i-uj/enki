from __future__ import annotations

import abc
import asyncio
import logging
import functools
from dataclasses import dataclass
from typing import Coroutine, List, Any, Optional

from enki.enkitype import Result

from enki import settings
from enki import devonly
from enki.net.kbeclient.message import MsgDescr, IMsgReceiver, Message
from enki.net.kbeclient.client import Client

logger = logging.getLogger(__name__)

TIMEOUT_ERROR_MSG = 'Timeout Error'


@dataclass
class CommandResult(Result):
    @property
    def success(self) -> bool:
        return None

    @property
    def result(self) -> Any:
        return None

    @property
    def text(self) -> str:
        return None



@dataclass
class _RequestData:
    @property
    def sent_msg_spec(self) -> MsgDescr:
        return None

    @property
    def success_msg_spec(self) -> Optional[MsgDescr]:
        return None

    @property
    def error_msg_specs(self) -> List[MsgDescr]:
        return None

    @property
    def future(self) -> asyncio.Future:
        return None

    @property
    def timeout(self) -> float:
        return None



class ICommand(abc.ABC):

    @abc.abstractmethod
    def execute(self) -> Any:
        pass


class IAwaitableCommand(ICommand):

    @property
    @abc.abstractmethod
    def waiting_for_ids(self) -> list[int]:
        pass

    @abc.abstractmethod
    def get_timeout_err_text(self) -> str:
        pass


class Command(IAwaitableCommand, IMsgReceiver):
    """Base class for commands.

    The command is a request-response communication approach between
    the client and the server. A descendent class encapsulates request and
    response data and gives the asynchronous interface to use the "execute"
    command method like a coroutine.

    A descendent should override the "execute" method and set the response and
    request messages to the variables below.
    """
    @property
    def _req_msg_spec(self) -> MsgDescr:
        return None

    @property
    def _success_resp_msg_spec(self) -> Optional[MsgDescr]:
        return None

    @property
    def _error_resp_msg_specs(self) -> list[MsgDescr]:
        return None


    def __init__(self, client: Client):
        self._client = client
        self._req_data_by_msg_id: dict[int, _RequestData] = {}

    def on_receive_msg(self, msg: Message) -> bool:
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
                     ) -> Coroutine[None, None, Optional[Message]]:
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
        except (asyncio.TimeoutError, asyncio.CancelledError):
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
