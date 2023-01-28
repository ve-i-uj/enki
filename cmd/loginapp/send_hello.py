import asyncio
import logging

from enki import settings
from enki.enkitype import AppAddr
from enki.net import msgspec
from enki.net.kbeclient import Client
from enki.net.command.loginapp import HelloCommand
from enki.misc import log

logger = logging.getLogger(__name__)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    try:
        client = Client(settings.LOGIN_APP_ADDR, msgspec.app.client.SPEC_BY_ID)
        res = await client.start()
        if not res.success:
            logger.error(f'Cannot connect to the "{settings.LOGIN_APP_ADDR}" server address '
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
