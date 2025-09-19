"""Тесты утилиты по чтению сериализованных сообщений в виде 16-ых байтов."""

import subprocess


class TestHexReder:
    """Тесты утилиты по чтению сериализованных сообщений в виде 16-ых байтов."""

    def test_read_msg(self):
        """Тест чтения сообщения."""
        command = [
            "python",
            "tools/msgreader",
            "hex",
            "client",
            "f6012a0031323300302e302e302e30002f4e180000006b62656e67696e655f636f636f7332645f6a735f64656d6f",
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 0
        assert result.stdout.strip().endswith(
            "Message(id=502, name=Client::onLoginSuccessfully)"
        )

    def test_read_msg_id(self):
        """Чтение только id сообщения."""
        command = [
            "python",
            "tools/msgreader",
            "hex",
            "client",
            "f6012a0031323300302e302e302e30002f4e180000006b62656e67696e655f636f636f7332645f6a735f64656d6f",
            "--whatis",
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 0
        assert result.stdout.strip().endswith("The message id is '502'")

    def test_no_envelop_msg_name(self):
        """Чтение сообщения без обёртки."""
        command = [
            "python",
            "tools/msgreader",
            "hex",
            "machine",
            "e80300006b62656e67696e650001000000a10f0000000000000200000000000000ffffffffffffffffffffffffac120006c5a3000000000000001c00000000000000000000000050c2010000000000000000000000000000000000000000000000000000000000007d000000000000ac1200064f76",
            "--no-envelop-msg-name",
            "Machine::onBroadcastInterface",
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 0
        assert result.stdout.strip().endswith(
            "Message(id=8, name=Machine::onBroadcastInterface)"
        )
