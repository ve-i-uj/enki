import asyncio
import logging

import environs

from enki import msgspec, settings
from enki.command.loginapp import LoginappHelloCommand
from enki.misc import log
from enki.msg.msg_client import TcpMsgClient
from enki.net import server
from enki.net.addr import Addr

logger = logging.getLogger(__name__)

_env = environs.Env()
_LOGINAPP_HOST: str = _env.str("KBE_LOGINAPP_HOST", "")
if _LOGINAPP_HOST == "":
    _LOGINAPP_HOST: str = _env.str("KBE_COMPONENT_NAME", "")
assert _LOGINAPP_HOST != "", (
    "The Loginapp host is not set. Set remote host "
    'variable "KBE_LOGINAPP_HOST" or "KBE_COMPONENT_NAME" variable'
)
_LOGINAPP_PORT: int = _env.int("KBE_LOGINAPP_TCP_PORT")
LOGINAPP_ADDR = Addr(_LOGINAPP_HOST, _LOGINAPP_PORT)


async def main() -> None:
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    host = server.get_real_host_ip(LOGINAPP_ADDR.ip_addr)
    addr = Addr(host, LOGINAPP_ADDR.port)
    try:
        client = TcpMsgClient(addr, msgspec.client.SPEC_BY_ID)
        res = await client.start()
        if not res.success:
            logger.error(
                f'Cannot connect to the "{addr}" server address (err="{res.text}")'
            )
            return

        cmd_4 = LoginappHelloCommand(
            kbe_version="2.5.10",
            script_version="0.1.0",
            encrypted_key=b"",
            client=client,
        )
        client.set_msg_receiver(cmd_4)
        resp_4 = await cmd_4.execute()
        if not resp_4.success:
            logger.error(f'No response (err="{resp_4.text}")')
            return

        logger.info(f"Done (result = {resp_4.result})")
    except Exception as err:
        logger.error(err, exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
