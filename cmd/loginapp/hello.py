import asyncio
import logging

import environs

from enki import settings
from enki.core.enkitype import AppAddr
from enki.core import msgspec
from enki.net.client import MsgTCPClient
from enki.command.loginapp import HelloCommand
from enki.misc import log

logger = logging.getLogger(__name__)

_env = environs.Env()
_LOGINAPP_HOST: str = _env.str('LOGINAPP_HOST')
_LOGIN_APP_PORT: int = _env.int('LOGIN_APP_PORT')
LOGIN_APP_ADDR = AppAddr(_LOGINAPP_HOST, _LOGIN_APP_PORT)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    try:
        client = MsgTCPClient(LOGIN_APP_ADDR, msgspec.app.client.SPEC_BY_ID)
        res = await client.start()
        if not res.success:
            logger.error(f'Cannot connect to the "{LOGIN_APP_ADDR}" server address '
                         f'(err="{res.text}")')
            return

        cmd_4 = HelloCommand(
            kbe_version='2.5.10',
            script_version='0.1.0',
            encrypted_key=b'',
            client=client
        )
        client.set_msg_receiver(cmd_4)
        resp_4 = await cmd_4.execute()
        if not resp_4.success:
            logger.error(f'No response (err="{resp_4.text}")')
            return

        logger.info(f'Done (result = {resp_4.result})')
    except Exception as err:
        logger.error(err, exc_info=True)


if __name__ == '__main__':
    asyncio.run(main())
