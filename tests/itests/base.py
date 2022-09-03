"""???"""

import asynctest

from enki.app import appl
from enki import settings
from enki.interface import IApp


class IntegrationBaseAppBaseTestCase(asynctest.TestCase):

    async def setUp(self) -> None:
        app = appl.App(settings.LOGIN_APP_ADDR, settings.SERVER_TICK_PERIOD)
        start_res = await app.start(settings.ACCOUNT_NAME, settings.PASSWORD)
        assert start_res.success, start_res.text
        self._app = app

    async def tearDown(self) -> None:
        if getattr(self, '_app', None) is None:
            return
        await self._app.stop()

    @property
    def app(self) -> IApp:
        return self._app
