"""Точка входа для кодо генератора клиентского плагина KBEngine на Python."""

import asyncio
import logging
import sys

from environs import Env, EnvError

from enki.misc import log
from enki.net.addr import Addr, Port

logger = logging.getLogger(__name__)




async def main() -> None:
    """Точка входа для запуска скрипта."""
    log.setup_root_logger(logging.getLevelName(LOG_LEVEL))

    env = Env()
    got_error = False

    game_account_name = ""
    try:
        game_account_name = env.str("GAME_ACCOUNT_NAME")
    except EnvError     as err:
        got_error = True
        logger.error(err)

    game_assets_dir = ""
    try:
        game_assets_dir = env.str("GAME_ASSETS_DIR")
    except EnvError     as err:
        got_error = True
        logger.error(err)

    game_password = ""
    try:
        game_password = env.str("GAME_PASSWORD")
    except EnvError as err:
        got_error = True
        logger.error(err)

    kbe_loginapp_host = ""
    try:
        kbe_loginapp_host = env.str("KBE_LOGINAPP_HOST")
    except EnvError as err:
        got_error = True
        logger.warning(err)

    kbe_loginapp_tcp_port = 0
    try:
        kbe_loginapp_tcp_port = env.int("KBE_LOGINAPP_TCP_PORT")
    except EnvError as err:
        got_error = True
        logger.warning(err)

    if got_error:
        logger.error("Failed to load environment variables")
        sys.exit(1)

    await generate_code(
        game_assets_dir,
        game_account_name,
        game_password,
        Addr(kbe_loginapp_host, Port(kbe_loginapp_tcp_port)),
    )


if __name__ == "__main__":
    asyncio.run(main())
