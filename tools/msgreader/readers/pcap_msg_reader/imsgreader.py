"""Интерфейсы для сервисов приложения.

Приложение читает пакеты транспортного уровня с сериализованными
KBEngine-сообщениями и отображает их в человекочитаемом виде.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from tools.msgreader.readers.pcap_msg_reader.pcap_file_chunker.online_pcap_file_reader import (
        NetChunkData,
    )

logger = logging.getLogger(__name__)


class PcapMsgReader:
    """Приложение читает KBEngine-сообщения из пакетов транспортного уровня."""

    def __init__(self, pcap_files_directory: Path, mapping_file: Path) -> None:
        """Конструктор.

        Args:
            pcap_files_directory (Path): путь до директории, содержащей
                pcap-файлы с KBEngine-сообщениями
            mapping_file (Path): файл, содержащий мапинг ip-адреса
                KBEngine-компонента к имени компонента

        """
        assert pcap_files_directory.is_dir(), "The path should be a directory"
        self._pcap_files_directory = pcap_files_directory
        self._mapping_file = mapping_file

    async def start(self) -> bool:
        """Запустить чтение pcap-файлов и их отображение."""
        for pcap_file_path in self._pcap_files_directory.iterdir():
            if not pcap_file_path.is_file() or pcap_file_path.suffix != ".pcap":
                logger.debug("[%s] The path '%s' is not a pcap-file. Skip", self)
                continue



        return False

    async def _start_pcap_reading(self, pcap_file_path: Path) -> bool:
        """Запустить чтение pcap-файла."""
        return False


class Pcap2NetChunkDataProducerCancelledExeption(Exception):
    """Исключение, возникающее при отмене операции получения или ожидания чанка.

    Это исключение выбрасывается, когда операция получения сетевого чанка (produce)
    была отменена (например, из-за CancelledError). Обычно это происходит при
    остановке или прерывании работы сервиса во время ожидания новых данных.

    Attributes:
        message: Описание ошибки (наследуется от базового класса Exception)

    """



class Pcap2NetChunkDataProducerIsNotStartedExeption(Exception):
    """Исключение, возникающее при попытке использования не запущенного сервиса.

    Это исключение выбрасывается, когда вызываются методы stop() или produce()
    до того, как сервис был запущен с помощью метода start(). Гарантирует, что
    сервис будет использоваться только в правильном состоянии.

    Attributes:
        message: Описание ошибки (наследуется от базового класса Exception)

    """


class IPcap2NetChunkDataProducer(ABC):
    """Абстрактный сервис для чтения pcap-файлов и производства сетевых пакетов."""

    @abstractmethod
    async def start(self) -> None:
        """Запускает процесс чтения pcap-файла и производства чанков.

        Raises:
            Pcap2NetChunkDataProducerAlreadyStartedExeption: если сервис уже
                запущен
            Pcap2NetChunkDataProducerAlreadyFinishedExeption: если сервис уже
                был завершен

        """

    @abstractmethod
    async def produce(self) -> NetChunkData | None:
        """Производит следующий сетевой чанк.

        Returns:
            NetChunkData: следующий сетевой чанк данных или None, если процесс
                чтения pcap-файла закончен

        Raises:
            Pcap2NetChunkDataProducerIsNotStartedExeption: если сервис не запущен
            Pcap2NetChunkDataProducerCancelledExeption: если операция была отменена

        """

    @abstractmethod
    async def stop(self) -> None:
        """Останавливает процесс чтения pcap-файла и производства чанков.

        Raises:
            Pcap2NetChunkDataProducerIsNotStartedExeption: если сервис не был
                запущен

        """

    @abstractmethod
    async def wait_until_stop(self) -> None:
        """Ожидает полной остановки и финализации сервиса.

        Метод блокируется до тех пор, пока сервис не завершит все операции
        и не освободит все ресурсы.
        """


class INetChunkDataConsumer(ABC):
    """Сервис агрегирует данные сетевых пакетов с KBEngine-сообщениями."""

    @abstractmethod
    def consume(self, net_chunk_data: NetChunkData):
        pass


class NetChunk2MsgDataProducer:
    """Сервис производит десериализованные KBEngine-сообщения из данных пакета."""


class MsgDataConsumer:
    """Агрегатор десериализованных KBEngine-сообщений из сетевых пакетов."""


class MsgDataRepresentator:
    """Сервис для отображения данных KBEngine-сообщения для пользователя."""
