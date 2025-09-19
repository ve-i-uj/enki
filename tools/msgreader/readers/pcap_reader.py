"""Чтение KBEngine-сообщений из pcap-файлов."""

from pathlib import Path


class PcapReader:
    """Читает KBEngine-сообщения из pcap-файлов."""

    def __init__(self, pcap_path: Path) -> None:
        pass

    def read(self) -> bool:
        """Прочитать весь pcap-файл."""
        return False

    def read_stream(self) -> None:
        """Читает новые данные добавленные в файл."""
