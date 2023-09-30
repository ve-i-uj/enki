"""Оправить компоненту сообщение об остановке.

Для работы этой команды сперва нужно узнать внутренний адрес компонента,
т.к. соединения из вне скидываются (reqCloseServer работает только у INTERNAL
подключений).
"""

import asyncio
import logging
import sys
import logging
from types import ModuleType

import environs

from enki import settings
from enki.core.enkitype import AppAddr
from enki.core.kbeenum import ComponentType
from enki.misc import log
from enki.net import server
from enki.core import msgspec
from enki.core.enkitype import AppAddr, Result
from enki.core.kbeenum import ComponentType
from enki.core.message import Message
from enki.command import RequestCommand
from enki.misc import devonly
from enki.net import server

from tools.cmd.common import utils
from tools.cmd.common.utils import NO_COMPONENT_ID, MachineAddr

logger = logging.getLogger(__name__)

_env = environs.Env()

KBE_MACHINE_HOST: str = _env.str('KBE_MACHINE_HOST')
KBE_MACHINE_UDP_PORT: int = _env.int('KBE_MACHINE_UDP_PORT', 20086)
KBE_MACHINE_TCP_PORT: int = _env.int('KBE_MACHINE_TCP_PORT', 20099)

KBE_COMPONENT_NAME: str = _env.str('KBE_COMPONENT_NAME')
KBE_COMPONENT_ID: int = _env.int('KBE_COMPONENT_ID', NO_COMPONENT_ID)


async def req_close_server(comp_type: ComponentType, host_ip: str,
                           machine_addr: MachineAddr) -> Result:
    """Отправить ::reqCloseServer на финализацию работы компонета."""
    logger.debug('%s', devonly.func_args_values())
    if comp_type.is_multiple_type():
        assert KBE_COMPONENT_ID != 0

    comp_info_res = await utils.request_comp_info(
        comp_type, KBE_COMPONENT_ID, machine_addr, host_ip
    )
    if not comp_info_res.success:
        # На Machine компонент не регистрировался, значит и не запушен
        return Result(False, None, comp_info_res.text)

    # В этой точке есть инфа о компоненте

    comp_info = comp_info_res.result
    assert comp_info is not None

    msg_spec_module: ModuleType = getattr(msgspec.app, comp_type.name.lower())
    cmd_reqCloseServer = RequestCommand(
        comp_info.internal_address,
        Message(msg_spec_module.reqCloseServer, tuple()),
        msgspec.custom.onReqCloseServer.change_component_owner(comp_type),
        stop_on_first_data_chunk=True
    )
    logger.info(f'Send request to stop to the {comp_type.name} component ...')
    res = await cmd_reqCloseServer.execute()

    if not res.success:
        # Компоненты в любом случае отправляют true. Если ничего не пришло,
        # значит адресат или скинул сообщение, или не получил, или клиент по таймауту
        logger.error(f'The component "{comp_type.name}" is unavailable '
                     f'(err={res.text}, address={comp_info.internal_address})')
        return Result(False, None, res.text)

    logger.info(f'The message to stop have been received by the '
                f'"{comp_type.name}" component')

    return Result(True, None)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    comp_type = getattr(ComponentType, KBE_COMPONENT_NAME.upper(), None)
    if comp_type is None:
        logger.error(f'Unknown component name "{KBE_COMPONENT_NAME}"')
        sys.exit(1)

    container_name: str = KBE_COMPONENT_NAME
    if comp_type.is_multiple_type():
        container_name = f'{KBE_COMPONENT_NAME}-{KBE_COMPONENT_ID}'
    logger.debug(f'The container name is "{container_name}"')

    res = await req_close_server(
        comp_type, server.get_real_host_ip(container_name),
        MachineAddr(
            KBE_MACHINE_HOST,
            KBE_MACHINE_TCP_PORT,
            KBE_MACHINE_UDP_PORT
        )
    )
    if not res.success:
        logger.error(res.text)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
