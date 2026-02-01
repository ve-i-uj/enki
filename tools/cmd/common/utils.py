"""Набор инструкментов для команд / скриптов."""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from enki import msgspec
from enki.apps.supervisor.supervisor_app import ComponentInfo
from enki.misc import devonly
from enki.misc.result import Result
from enki.msg.message import Message
from enki.msg.msg_client import RawRespUdpMsgClient
from enki.msg_parser.machine_msg_parser import (
    OnBroadcastInterfaceMsgParser,
    OnFindInterfaceAddrParsedMsgData,
)
from enki.net.addr import Addr, Port
from enki.settings import SECOND

if TYPE_CHECKING:
    from enki.kbeenum import ComponentType

logger = logging.getLogger(__name__)


class _CachedComponentInfo:
    """Обёртка над способом закэшировать данные компонента.

    Чтобы не забивать запросами Машину воспользуемся закэшированными
    данными о запрашиваемом компоненте.
    """

    def __init__(self) -> None:
        self._cached_data_dir = Path(tempfile.gettempdir()) / "enki" / "cache"
        self._cached_data_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, comp_type: ComponentType, comp_id: int) -> Path:
        """Возвращает путь, где хранится закэшированные данные компонента.

        Args:
            comp_type (ComponentType): тип компонента
            comp_id (int): id компонента

        Returns:
            Path: путь до кэшированных данных

        """
        cached_data_path = (
            self._cached_data_dir / f"{comp_type.name}-{comp_id}.cached"
        )
        cached_data_path.touch(exist_ok=True)
        return cached_data_path

    def get_comp_info(
        self, comp_type: ComponentType, comp_id: int
    ) -> ComponentInfo | None:
        """Получить закэшированную информацию о компоненте.

        Args:
            comp_type (ComponentType): тип компонента
            comp_id (int): id компонента

        Returns:
            ComponentInfo | None: информация о компоненте или None, если нет
                кэшированной информации

        """
        logger.debug("%s", devonly.func_args_values())

        comp_info: ComponentInfo | None = None
        cached_data_path = self._get_cache_path(comp_type, comp_id)

        logger.info("Read the %s cached info ...", comp_type.name)
        with cached_data_path.open() as fh:
            text = fh.read()
        try:
            comp_info = ComponentInfo.from_json(text)
            logger.info("The cached %s info exists", comp_type.name)
        except ValueError:
            logger.info(
                'There is no cached info in the "%s" file', cached_data_path
            )

        return comp_info

    def delete_comp_info(self, comp_type: ComponentType, comp_id: int) -> None:
        """Удалить информацию о закэшированном компоненте.

        Args:
            comp_type (ComponentType): тип компонента
            comp_id (int): id компонента

        """
        cached_data_path = self._get_cache_path(comp_type, comp_id)
        logger.info('Delete not actual cache file "%s"', cached_data_path)
        cached_data_path.unlink()

    def save_cache_info(self, comp_info: ComponentInfo) -> None:
        """Удалить информацию о закэшированном компоненте.

        Args:
            comp_info (ComponentInfo): информация о компоненте

        """
        cached_data_path = self._get_cache_path(
            comp_info.component_type, comp_info.componentID
        )
        logger.info('Save data to the cache file "%s"', cached_data_path)
        with cached_data_path.open("w") as fh:
            fh.write(comp_info.to_json(comp_info))


CachedComponentInfo = _CachedComponentInfo()


@dataclass
class MachineAddr:
    """Данные для подключения к Machine."""

    host: str
    tcp_port: Port
    udp_port: Port


@dataclass(frozen=True)
class ReqCompInfoResult(Result):
    """Результат запроса информации о компоненте у Machine."""

    success: bool
    result: ComponentInfo | None
    text: str = ""


async def request_comp_info(
    comp_type: ComponentType,
    component_id: int,
    machine_addr: MachineAddr,
) -> ReqCompInfoResult:
    """Запросить информацию о компоненте у Machine.

    Args:
        comp_type (ComponentType): тип компонента
        component_id (int): id компонента (cid)
        machine_addr (MachineAddr): адрес Machine

    Returns:
        ReqCompInfoResult: объект результата запроса

    """
    logger.debug("%s", devonly.func_args_values())
    logger.info("Request the internal %s address ...", comp_type.name)

    req_pd = OnFindInterfaceAddrParsedMsgData.get_empty()
    # Выставляется тип компонента, для которого нужно найти внутренний адрес
    req_pd.find_component_type = comp_type
    req_pd.find_component_id = component_id

    msg = Message.create(
        msgspec.machine.onFindInterfaceAddr, req_pd.get_values()
    )
    client = RawRespUdpMsgClient(
        Addr(machine_addr.host, Port(machine_addr.udp_port)),
        msgspec.machine.onBroadcastInterface,
    )
    res = await client.send_msg(msg)
    if not res:
        text = f"The message '{msg.name}' is not sent"
        return ReqCompInfoResult(success=False, result=None, text=text)

    comp_info: ComponentInfo | None = None
    async for resp_msg in client.wait_and_iterate_resp_msgs(2 * SECOND):
        result = OnBroadcastInterfaceMsgParser().parse(resp_msg)
        info = result.result
        if info.componentID == component_id:
            # Это данные компонента, который мы запрашивали
            comp_info = info
            break

    # Эта процедура используется для хэлсчека запущенного компонента.
    # Точно известен его id под которым он должен был зарегистрироваться
    # при старте. Если он не найден - это или компонент не стартанул,
    # или ошибка в логике.
    if comp_info is None:
        text = (
            f'There is no requested component "{comp_type.name}" '
            f"(cid={component_id})"
        )
        logger.info(text)
        return ReqCompInfoResult(success=False, result=None, text=text)

    res_text: str = (
        f"The response from Machine has been received. The internal "
        f'{comp_type.name} address is "{comp_info.internal_address}"'
    )
    logger.info(res_text)
    return ReqCompInfoResult(success=True, result=comp_info, text=res_text)
