"""Tests of FixedDict encoder / decoder."""

from dataclasses import dataclass
import unittest
from collections import OrderedDict

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


# [2026-02-05 17:00 burov_alexey@mail.ru]:
# Это уже создание пользовательских типов. Главное, что есть декодинг типа FD.
# А то что можно или нельзя какие-то поля добавлять - это другое. Наружу
# пользователю я могу отправлять и TypedDict с нужными полями. IKBEType - это
# внутренняя тема самого приложения, а не игры уже.
@pytest.mark.skip("Not implemented yet")
class FixedDictInitTestCase(unittest.TestCase):
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
class FixedDictUpdateTestCase(unittest.TestCase):
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
