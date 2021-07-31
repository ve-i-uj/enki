"""System manager."""

import abc
import asyncio
import contextlib
import datetime
import logging
from typing import Coroutine, Optional

from enki import command
from damkina import interface

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

    def __init__(self, app: interface.IApp, period: int):
        self._app = app
        self._period = period
        self._task: Optional[asyncio.Task] = None

    async def _periodic(self):
        while True:
            await asyncio.sleep(self._period)
            cmd = command.baseapp.OnClientActiveTickCommand(
                client=self._app.client,
                receiver=self._app,
                timeout=self._period
            )
            await self._app.send_command(cmd)

    def start(self):
        self._task = asyncio.ensure_future(self._periodic())

    async def stop(self):
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task


class SysMgr:
    """System manager."""

    def __init__(self, app: interface.IApp):
        self._app = app

        self._last_server_tick_time: datetime.datetime = datetime.datetime.now()
        self._server_tick: Optional[_ServerTickPeriodic] = None

    def start_server_tick(self, period: int):
        self._server_tick = _ServerTickPeriodic(self._app, period)
        self._server_tick.start()

    async def stop_server_tick(self):
        await self._server_tick.stop()
