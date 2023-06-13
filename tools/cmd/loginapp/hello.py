import asyncio
import logging

import environs

from enki import settings
from enki.core.enkitype import AppAddr
from enki.core import msgspec
from enki.net import server
from enki.net.client import MsgTCPClient
from enki.command.loginapp import HelloCommand
from enki.misc import log

logger = logging.getLogger(__name__)

_env = environs.Env()
_LOGINAPP_HOST: str = _env.str('LOGINAPP_HOST', '')
if _LOGINAPP_HOST == '':
    _LOGINAPP_HOST: str = _env.str('KBE_COMPONENT_NAME', '')
assert _LOGINAPP_HOST != '', 'The Loginapp host is not set. Set remote host ' \
    'variable "LOGINAPP_HOST" or "KBE_COMPONENT_NAME" variable'
_LOGINAPP_PORT: int = _env.int('LOGINAPP_PORT')
LOGINAPP_ADDR = AppAddr(_LOGINAPP_HOST, _LOGINAPP_PORT)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    host = server.get_real_host_ip(LOGINAPP_ADDR.host)
    addr = AppAddr(host, LOGINAPP_ADDR.port)
    try:
        client = MsgTCPClient(addr, msgspec.app.client.SPEC_BY_ID)
        res = await client.start()
        if not res.success:
            logger.error(f'Cannot connect to the "{addr}" server address '
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
