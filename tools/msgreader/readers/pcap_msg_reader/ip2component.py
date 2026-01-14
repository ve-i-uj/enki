"""Mapping of component IP addresses to KBEngine component types."""

import logging
from ipaddress import IPv4Address
from pathlib import Path

from enki.kbeenum import ComponentType

logger = logging.getLogger(__name__)


class Ip2ComponentType:
    """Maps IP addresses to KBEngine component types based on a configuration file.

    Each line should be in the format:
    component_name=<last ip octet>

    The logger host has the ip address 172.18.0.4. The last ip octet is 4.

    Example of the line in the file:
        supervisor=2
        logger=4
        interfaces=5
        dbmgr=6

    """

    def __init__(self, mapping_file: Path) -> None:
        """Initialize the IP to component type mapper.

        Args:
            mapping_file (Path): path to the configuration file containing
                IP patterns and their corresponding component names.

        """
        assert mapping_file.exists() and mapping_file.is_file(), (
            f"[{self}] The file doesn't exist or is not a file "
            f"(mapping file = '{mapping_file}')"
        )

        self._mapping_file = mapping_file
        self._comp_type_by_last_oktet: dict[int, ComponentType] = {}

    def load_mapping(self) -> None:
        with open(self._mapping_file) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue

                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    logger.warning(
                        "[%s] Invalid line. The line has no '='", self
                    )
                    continue

                comp_name, last_octet_str = line.split("=")

                if not last_octet_str.isnumeric():
                    logger.warning(
                        "[%s] Invalid line. The char after '=' is not a number",
                        self,
                    )
                    continue

                last_octet = int(last_octet_str)

                if not ComponentType.is_valid_name(comp_name):
                    logger.warning(
                        "[%s] Invalid line. There is no KBEngine component "
                        "with the name '%s'",
                        self,
                        comp_name,
                    )
                    continue

                self._comp_type_by_last_oktet[last_octet] = (
                    ComponentType.from_name(comp_name)
                )

    def get_component_type_by_ip_addr(
        self, ip_addr: IPv4Address
    ) -> ComponentType:
        """Determine the component type based on the IP address.

        Args:
            ip_addr: The IPv4 address to match against configured patterns.

        Returns:
            The matching component type, or ComponentType.UNKNOWN_COMPONENT
                if no match found.

        """
        if not self._comp_type_by_last_oktet:
            logger.warning(
                "[%s] There is no mapping. Empty file or not calling 'load_mapping'?",
                self,
            )

        ip_str = str(ip_addr)
        last_octet = int(ip_str.rsplit(".", 1)[-1])

        if last_octet not in self._comp_type_by_last_oktet:
            if last_octet != 255:
                logger.warning(
                    "[%s] The mapping has no KBEngine-component for last octet '%s'",
                    self,
                    last_octet,
                )
            return ComponentType.UNKNOWN_COMPONENT

        return self._comp_type_by_last_oktet[last_octet]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._mapping_file.name})"
