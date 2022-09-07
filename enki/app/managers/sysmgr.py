"""System manager."""

import abc
import asyncio
import contextlib
import datetime
import logging
from typing import Optional

from enki import command, descr, exception
from enki.interface import IApp, IResult
from enki.kbeclient.message import Message

logger = logging.getLogger(__name__)


class IPeriodic(abc.ABC):

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def _periodic(self):
        pass


class _ServerTickPeriodic(IPeriodic):

    def __init__(self, app: IApp, period: float):
        self._app = app
        self._period = period
        self._task: Optional[asyncio.Task] = None

    async def _periodic(self):
        while True:
            await asyncio.sleep(self._period)
            msg = Message(descr.app.client.onAppActiveTickCB, tuple())
            cmd = command.baseapp.OnClientActiveTickCommand(
                client=self._app.client,
                timeout=self._period
            )
            res: IResult = await self._app.send_command(cmd)
            # TODO: [12.10.2021 burov_alexey@mail.ru]:
            # Думаю, здесь значительно больше вариантов.
            if not res.success:
                msg = 'No connection with the server'
                logger.warning(f'[{self}] {msg}')
                break

        self._app.on_end_receive_msg()

    def start(self):
        self._task = asyncio.ensure_future(self._periodic())

    async def stop(self):
        if self._task is None:
            logger.warning(f'[{self}] The task has not been started')
            return
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(app={self._app}, period={self._period})'


class SysMgr:
    """System manager."""

    def __init__(self, app: IApp):
        self._app = app

        self._last_server_tick_time: datetime.datetime = datetime.datetime.now()
        self._server_tick: Optional[_ServerTickPeriodic] = None

    def start_server_tick(self, period: float):
        self._server_tick = _ServerTickPeriodic(self._app, period)
        self._server_tick.start()

    async def stop_server_tick(self):
        if self._server_tick is None:
            logger.warning(f'[{self}] The loop of the "onClientActiveTick" '
                           f'message has not beed started')
            return
        await self._server_tick.stop()
