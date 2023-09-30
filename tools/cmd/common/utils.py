"""Набор инструкментов для команд / скриптов."""

from dataclasses import dataclass
import logging
import platform
import tempfile
from pathlib import Path
from typing import Optional

from enki.core.enkitype import AppAddr, Result
from enki.core.kbeenum import ComponentType
from enki.command.machine import OnFindInterfaceAddrTCPCommand, \
    OnFindInterfaceAddrUDPCommand
from enki.handler.serverhandler.machinehandler import OnBroadcastInterfaceParsedData, \
    OnFindInterfaceAddrParsedData
from enki.misc import devonly
from enki.net import server

logger = logging.getLogger(__name__)

NO_COMPONENT_ID = 0

ComponentInfo = OnBroadcastInterfaceParsedData


class _CachedComponentInfo:
    """Обёртка над способом закэшировать данные компонента.

    Чтобы не забивать запросами Машину воспользуемся закэшированными
    данными о запрашиваемом компоненте.
    """

    def __init__(self) -> None:
        self._cached_data_dir = Path(
            "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
        ) / 'enki' / 'cache'
        self._cached_data_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, comp_type: ComponentType,
                        comp_id: int) -> Path:
        return self._cached_data_dir / f'{comp_type.name}-{comp_id}.cached'

    def get_comp_info(self, comp_type: ComponentType, comp_id: int) -> Optional[ComponentInfo]:
        logger.debug('%s', devonly.func_args_values())
        comp_info: Optional[ComponentInfo] = None
        cached_data_path = self._get_cache_path(comp_type, comp_id)
        cached_data_path.touch(exist_ok=True)
        logger.info(f'Read the {comp_type.name} cached info ...')
        with cached_data_path.open() as fh:
            text = fh.read()
        try:
            comp_info = ComponentInfo.from_json(text)
            logger.info(f'The cached {comp_type.name} info exists')
        except ValueError:
            logger.info(f'There is no cached info in the "{cached_data_path}" file')

        return comp_info

    def delete_comp_info(self, comp_type: ComponentType, comp_id: int):
        cached_data_path = self._get_cache_path(comp_type, comp_id)
        logger.info(f'Delete not actual cache file "{cached_data_path}"')
        cached_data_path.unlink()

    def save_cache_info(self, comp_info: ComponentInfo):
        cached_data_path = self._get_cache_path(
            comp_info.component_type, comp_info.componentID
        )
        logger.info(f'Save data to the cache file "{cached_data_path}"')
        with cached_data_path.open('w') as fh:
            fh.write(comp_info.to_json(comp_info))


CachedComponentInfo = _CachedComponentInfo()


@dataclass
class MachineAddr:
    host: str
    tcp_port: int
    udp_port: int


@dataclass
class ReqCompInfoResult(Result):
    success: bool
    result: Optional[ComponentInfo]
    text: str = ''


async def request_comp_info(comp_type: ComponentType, component_id: int,
                            machine_addr: MachineAddr, host_ip: str
                            ) -> ReqCompInfoResult:
    """Запросить информацию о компоненте от Machine."""
    logger.debug('%s', devonly.func_args_values())
    logger.info(f'Request the internal {comp_type.name} address ...')
    comp_info: Optional[ComponentInfo] = None
    req_pd = OnFindInterfaceAddrParsedData(
        uid=1000,
        username='root',
        componentType=ComponentType.UNKNOWN_COMPONENT,
        componentID=0,
        findComponentType=comp_type.value,
        addr=0,
        finderRecvPort=0
    )
    if comp_type.is_multiple_type():
        cmd = OnFindInterfaceAddrTCPCommand(
            AppAddr(machine_addr.host, machine_addr.tcp_port),
            req_pd
        )
        res = await cmd.execute()
        if not res.success:
            text = f'No response from Machine (err="{res.text}")'
            return ReqCompInfoResult(False, None, text)

        comp_info: Optional[ComponentInfo] = None
        for info in res.result.infos:
            # Это данные компонента, который мы запрашивали
            if info.componentID == component_id:
                comp_info = info
                break
        # Эта процедура используется для хэлсчека запущенного компонента.
        # Точно известен его id под которым он должен был зарегистрироваться
        # при старте. Если он не найден - это или компонент не стартанул,
        # или ошибка в логике.
        if comp_info is None:
            text = (f'There is no reqistered component "{comp_type}" '
                            f'(cid={component_id})')
            return ReqCompInfoResult(False, None, text)
    else:
        req_pd.callback_address = AppAddr(host_ip, server.get_free_port())
        cmd = OnFindInterfaceAddrUDPCommand(
            AppAddr(machine_addr.host, machine_addr.udp_port),
            req_pd
        )
        res = await cmd.execute()
        if not res.success:
            text = f'No response from Machine (err="{res.text}")'
            return ReqCompInfoResult(False, None, text)
        comp_info = res.result
        assert comp_info is not None

    if comp_info.component_type == ComponentType.UNKNOWN_COMPONENT:
        text = f'The component "{comp_type.name}" is not registered'
        return ReqCompInfoResult(False, None, text)

    text: str = (f'The response from Machine has been received. The internal '
                 f'{comp_type.name} address is "{comp_info.internal_address}"')
    logger.info(text)

    return ReqCompInfoResult(True, comp_info, text)
