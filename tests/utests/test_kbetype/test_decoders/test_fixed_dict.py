"""Tests of KBEngine FixedDict encoder / decoder."""

from collections import OrderedDict
from dataclasses import dataclass

import pytest

from enki.kbetype.decoders.basic_data_type_decoders import (
    INT32,
    UNICODE,
)
from enki.kbetype.decoders.collection_decoders import (
    FIXED_DICT,
    FixedDictDecoders,
)
from enki.kbetype.decoders.custom_decoders import DBID, KBEDbid
from enki.kbetype.pytypes.basic_data_types import KBEInt32, KBEUnicode
from enki.kbetype.pytypes.collections import KBEFixedDict


@dataclass
class AvatarInfoFixedDict(KBEFixedDict):
    name: KBEUnicode
    uid: KBEInt32
    dbid: KBEDbid


@dataclass
class AvatarInfoFixedDictDecoders(FixedDictDecoders):
    name: type[UNICODE] = UNICODE
    uid: type[INT32] = INT32
    dbid: type[DBID] = DBID


class AVATAR_INFO(FIXED_DICT[AvatarInfoFixedDict, AvatarInfoFixedDictDecoders]):
    _result_type = AvatarInfoFixedDict
    _decoders = AvatarInfoFixedDictDecoders


class TestFixedDict:
    """Tests for FixedDict."""

    def test_decode_empty(self):
        """Test empty FD decoding."""
        fixed_dict = AVATAR_INFO

        data = memoryview(
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        )
        value, offset = fixed_dict.decode(data)
        assert offset != 0
        assert isinstance(value, AvatarInfoFixedDict)

        assert value.name == ""
        assert isinstance(value.name, KBEUnicode)
        assert value.uid == 0
        assert isinstance(value.uid, KBEInt32)
        assert value.dbid == 0
        assert isinstance(value.dbid, KBEDbid)

    def test_encode_empty(self):
        """Test encoding empty FixedDict."""
        empty_fd = AvatarInfoFixedDict(
            name=KBEUnicode(""), uid=KBEInt32(0), dbid=KBEDbid(0)
        )

        encoded = AVATAR_INFO.encode(empty_fd)

        expected = (
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        )
        assert encoded == expected

    def test_decode(self):
        """Test FD decoding."""
        data = memoryview(
            b"\x06\x00\x00\x00QWERTY\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00"
        )
        value, offset = AVATAR_INFO.decode(data)
        assert offset != 0
        assert isinstance(value, AvatarInfoFixedDict)

        assert value.name == "QWERTY"
        assert isinstance(value.name, KBEUnicode)
        assert value.uid == 1
        assert isinstance(value.uid, KBEInt32)
        assert value.dbid == 2
        assert isinstance(value.dbid, KBEDbid)

    def test_encode_with_values(self):
        """Test encoding FixedDict with values."""
        # Создаем FixedDict с данными
        fd = AvatarInfoFixedDict(
            name=KBEUnicode("QWERTY"), uid=KBEInt32(1), dbid=KBEDbid(2)
        )

        # Кодируем
        encoded = AVATAR_INFO.encode(fd)

        # Проверяем результат
        expected = b"\x06\x00\x00\x00QWERTY\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00"
        assert encoded == expected

    def test_encode_decode_roundtrip(self):
        """Test that encode/decode are inverses."""
        # Исходные данные
        original_fd = AvatarInfoFixedDict(
            name=KBEUnicode("TestUser"),
            uid=KBEInt32(42),
            dbid=KBEDbid(1234567890),
        )

        # Кодируем
        encoded = AVATAR_INFO.encode(original_fd)

        # Декодируем обратно
        decoded_fd, offset = AVATAR_INFO.decode(memoryview(encoded))

        # Проверяем, что offset равен длине закодированных данных
        assert offset == len(encoded)

        # Проверяем, что данные совпадают
        assert decoded_fd.name == original_fd.name
        assert decoded_fd.uid == original_fd.uid
        assert decoded_fd.dbid == original_fd.dbid

    def test_encode_with_special_characters(self):
        """Test encoding FixedDict with special characters in string."""
        fd = AvatarInfoFixedDict(
            name=KBEUnicode("Тест 😀"), uid=KBEInt32(100), dbid=KBEDbid(999)
        )

        encoded = AVATAR_INFO.encode(fd)

        # Декодируем обратно для проверки
        decoded_fd, _ = AVATAR_INFO.decode(memoryview(encoded))

        assert decoded_fd.name == "Тест 😀"
        assert decoded_fd.uid == 100
        assert decoded_fd.dbid == 999

    def test_encode_max_values(self):
        """Test encoding with maximum values."""
        fd = AvatarInfoFixedDict(
            name=KBEUnicode("A" * 100),  # длинная строка
            uid=KBEInt32(2**31 - 1),  # максимальное int32
            dbid=KBEDbid(2**63 - 1),  # максимальное int64
        )

        encoded = AVATAR_INFO.encode(fd)

        # Декодируем обратно для проверки
        decoded_fd, _ = AVATAR_INFO.decode(memoryview(encoded))

        assert decoded_fd.name == "A" * 100
        assert decoded_fd.uid == 2**31 - 1
        assert decoded_fd.dbid == 2**63 - 1

    def test_encode_order_preservation(self):
        """Test that encoding preserves field order from FixedDictDecoders."""
        fd = AvatarInfoFixedDict(
            name=KBEUnicode("OrderTest"), uid=KBEInt32(1), dbid=KBEDbid(2)
        )

        encoded = AVATAR_INFO.encode(fd)

        data = memoryview(encoded)

        # name
        name_value, offset = UNICODE.decode(data)
        assert name_value == "OrderTest"
        data = data[offset:]

        # uid
        uid_value, offset = INT32.decode(data)
        assert uid_value == 1
        data = data[offset:]

        # dbid
        dbid_value, offset = DBID.decode(data)
        assert dbid_value == 2


# [2026-02-05 17:00 burov_alexey@mail.ru]:
# Это уже создание пользовательских типов. Главное, что есть декодинг типа FD.
# А то что можно или нельзя какие-то поля добавлять - это другое. Наружу
# пользователю я могу отправлять и TypedDict с нужными полями. IKBEType - это
# внутренняя тема самого приложения, а не игры уже.
@pytest.mark.skip("Not implemented yet")
class TestFixedDictInit:
    """Initialization of FixedDict."""

    def setUp(self):
        super().setUp()

    def test_negative_no_args(self):
        with pytest.raises(TypeError):
            FixedDict()

    def test_init(self):
        fd = FixedDict("UNITTEST_TYPE", OrderedDict([("x", 0), ("y", 0)]))
        assert fd._data == OrderedDict([("x", 0), ("y", 0)])

    def test_fd_is_plugin_type(self):
        """FixedDict should be a plugin type."""
        FixedDict("UNITTEST_TYPE", OrderedDict([("x", 0), ("y", 0)]))
        # TODO: [2025-06-25 11:59 burov_alexey@mail.ru]:
        # Вернуть проверку на тип, если она будет нужна
        # self.assertIsInstance(fd, EnkiType)

    def test_negative_init_dict(self):
        """Dict in constructor."""
        with pytest.raises(TypeError):
            FixedDict("UNITTEST_TYPE", {"name": "", "uid": 0})


@pytest.mark.skip("Not implemented yet")
class TestFixedDictUpdate:
    """Tests of FixedDict updating."""

    def test_change_value(self):
        fd = FixedDict(
            "UNITTEST_TYPE",
            OrderedDict([("name", "name"), ("uid", 123), ("dbid", 56)]),
        )
        fd["uid"] = 0
        assert fd._data == OrderedDict(
            [("name", "name"), ("uid", 0), ("dbid", 56)]
        )

    def test_negative_invalid_value_type(self):
        fd = FixedDict(
            "UNITTEST_TYPE",
            OrderedDict([("name", "name"), ("uid", 123), ("dbid", 56)]),
        )
        with pytest.raises(KeyError):
            fd["uid"] = "string"
        # Values is the same
        assert fd._data == OrderedDict(
            [("name", "name"), ("uid", 123), ("dbid", 56)]
        )
