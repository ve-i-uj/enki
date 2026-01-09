"""Маппинг ip-адресов компонентов к типу KBEngine-компонента."""

from ipaddress import IPv4Address
from pathlib import Path

from enki.kbeenum import ComponentType


class Ip2ComponentType:
    """Маппинг ip-адресов компонентов к типу KBEngine-компонента."""

    def __init__(self, mapping_file: Path) -> None:
        pass

    def get_component_type_by_ip_addr(
        self, ip_addr: IPv4Address
    ) -> ComponentType:
        return ComponentType.UNKNOWN_COMPONENT
