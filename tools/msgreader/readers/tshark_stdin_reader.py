"""Чтение серилизованных сообщений из stdin."""

from __future__ import annotations

import logging
import sys
import time
from typing import TYPE_CHECKING

import dateutil.parser

from tools.msgreader.deserializers import deserialize_msg

if TYPE_CHECKING:
    from pathlib import Path

    from enki.kbeenum import ComponentType

logger = logging.getLogger(__name__)


def read_from_stdin(comp_type: ComponentType) -> None:
    timeout = 0.1
    try:
        for stdin_line in iter(sys.stdin.readline, b""):
            line = stdin_line.strip()
            if not line:
                logger.debug("There is no data. Sleep 1 second")
                time.sleep(timeout)
                continue

            dt_str, src_ip, dst_ip, _src_port, _dst_port, hex_data = line.split(
                "|"
            )
            dateutil.parser.parse(dt_str)

            logger.debug("Receive hex stream (data = %s)", line)
            data = _normalize_wireshark_data(hex_data)
            logger.debug("Receive data (data = %s)", data)

            if not data:
                continue

            msg_name = None
            if src_ip == dst_ip and len(data) != 2:
                # TODO: [2025-08-31 16:34 burov_alexey@mail.ru]:
                # Пока так.
                # Это проверка контейнера, поэтому это или из контейнера
                # приходит lookApp, или ответ в виде стрима onLookApp
                msg_name = f"{comp_type.name.capitalize()}::onLookApp"

            deserialize_msg(
                memoryview(data),
                no_envelop_msg_name=msg_name,
                only_find_msg_id=False,
                comp_type=comp_type,
            )
    except KeyboardInterrupt:
        sys.stdout.flush()


"""Чтение KBEngine-сообщений из pcap-файлов."""



class PcapReader:
    """Читает KBEngine-сообщения из pcap-файлов."""

    def __init__(self, pcap_path: Path) -> None:
        pass

    def read(self) -> bool:
        """Прочитать весь pcap-файл."""
        return False

    def read_stream(self) -> None:
        """Читает новые данные добавленные в файл."""
