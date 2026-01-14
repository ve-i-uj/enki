"""Тесты для класса PcapFileStem."""

from ipaddress import IPv4Address
from unittest.mock import patch

import pytest

from enki.kbeenum import ComponentType
from tools.msgreader.readers.pcap_msg_reader.pcap_file_chunker.pcap_file_stem import (
    PcapFileStem,
)


class TestPcapFileStem:
    """Тесты для класса PcapFileStem."""

    def test_valid_constructor_success(self):
        """Тест успешного создания объекта с валидным именем файла."""
        # Arrange
        filename_stem = "loginapp-1-192.168.1.1"

        # Act
        pcap_stem = PcapFileStem(filename_stem)

        # Assert
        assert pcap_stem.component_type == ComponentType.LOGINAPP
        assert pcap_stem.component_id == 1
        assert pcap_stem.host_ip_addr == IPv4Address("192.168.1.1")
        assert str(pcap_stem) == filename_stem

    def test_constructor_invalid_format_raises_error(self):
        """Тест, что невалидный формат вызывает ошибку."""
        invalid_stems = [
            "loginapp-1",  # недостаточно частей
            "loginapp",  # только имя
            "",  # пустая строка
            "-1-192.168.1.1",  # отсутствует имя компонента
        ]

        for stem in invalid_stems:
            with pytest.raises(AssertionError, match="Invalid file name"):
                PcapFileStem(stem)

    def test_validate_correct(self):
        """Тест валидации правильных имен."""
        valid_cases = [
            "loginapp-1-192.168.1.1",
            "baseapp-100-10.0.0.255",
            "cellapp-999-172.16.0.1",
        ]

        for stem in valid_cases:
            # Нужно замокать проверку имени компонента
            assert PcapFileStem.validate(stem) is True

    def test_validate_invalid_ip_address(self):
        """Тест валидации с неверным IP адресом."""
        invalid_cases = [
            "loginapp-1-999.999.999.999",
            "loginapp-1-192.168.1.256",
            "loginapp-1-not-an-ip",
            "loginapp-1-192.168.1",  # неполный IP
            "loginapp-1-192.168.1.1.1",  # слишком много октетов
        ]

        for stem in invalid_cases:
            assert PcapFileStem.validate(stem) is False

    def test_validate_invalid_component_id(self):
        """Тест валидации с неверным component_id."""
        invalid_cases = [
            "loginapp-abc-192.168.1.1",
            "loginapp--192.168.1.1",  # пустой ID
            "loginapp-1.5-192.168.1.1",  # не целое число
            "loginapp--1-192.168.1.1",  # отрицательное число (строкой)
        ]

        for stem in invalid_cases:
            assert PcapFileStem.validate(stem) is False

    def test_validate_invalid_component_name(self):
        """Тест валидации с неверным именем компонента."""
        filename_stem = "invalid_component-1-192.168.1.1"

        assert PcapFileStem.validate(filename_stem) is False

    def test_properties(self):
        """Тест свойств (properties) объекта."""
        # Arrange
        filename_stem = "baseapp-42-10.0.0.1"

        # Act
        pcap_stem = PcapFileStem(filename_stem)

        # Assert
        assert pcap_stem.component_id == 42
        assert pcap_stem.host_ip_addr == IPv4Address("10.0.0.1")
        assert pcap_stem.component_type == ComponentType.BASEAPP


class TestPcapFileStemEdgeCases:
    """Тесты для граничных случаев и обработки ошибок."""

    def test_large_component_id(self):
        """Тест с большим component_id."""
        filename_stem = "loginapp-999999-192.168.1.1"

        pcap_stem = PcapFileStem(filename_stem)
        assert pcap_stem.component_id == 999999

    def test_ipv6_address_not_supported(self):
        """Тест, что IPv6 адреса не поддерживаются (используется IPv4Address)."""
        filename_stem = "loginapp-1-2001:0db8::1"

        assert PcapFileStem.validate(filename_stem) is False
