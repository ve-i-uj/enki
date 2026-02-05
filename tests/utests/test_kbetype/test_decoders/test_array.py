"""Tests of FixedDict encoder / decoder."""

import collections
from dataclasses import dataclass
import dataclasses
import unittest
from typing import TypeAlias

import pytest

from enki.kbetype.decoders.basic_data_type_decoders import (
    INT32,
    STRING,
    UNICODE,
)
from enki.kbetype.decoders.collection_decoders import (
    ARRAY,
    FIXED_DICT,
    FixedDictDecoders,
)
from enki.kbetype.decoders.custom_decoders import DBID, KBEDbid
from enki.kbetype.pytypes.basic_data_types import (
    KBEInt32,
    KBEUInt32,
    KBEUnicode,
)
from enki.kbetype.pytypes.collections import KBEArray, KBEFixedDict

Int32Array: TypeAlias = KBEArray[KBEInt32]
Int32ArrayList: TypeAlias = list[KBEInt32]


class INT32_ARRAY(ARRAY[KBEInt32, INT32]):
    """Декодер для типа массива INT."""

    @classmethod
    def _get_element_decoder(cls) -> type[INT32]:
        return INT32


class UNICODE_ARRAY(ARRAY[KBEUnicode, UNICODE]):
    """Декодер для типа массива UNICODE."""

    _element_decoder = UNICODE


class STRING_ARRAY(ARRAY[KBEUnicode, STRING]):
    """Декодер для типа массива STRING."""

    _element_decoder = STRING


class ArrayTypeTestCase(unittest.TestCase):
    """Tests for KBEArray."""

    def setUp(self):
        super().setUp()

    def test_decode_empty(self):
        """Test of empty array decoding."""
        decoder = INT32_ARRAY
        data = memoryview(b"\x00\x00\x00\x00")
        value, offset = decoder.decode(data)

        assert offset != 0
        assert isinstance(value, KBEArray)
        assert not value

    def test_decode(self):
        """Test FD decoding."""
        decoder = INT32_ARRAY

        data = memoryview(
            b"\x04\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00"
        )
        values, offset = decoder.decode(data)

        assert offset == 20
        assert isinstance(values, KBEArray)
        assert len(values) == 4
        assert isinstance(values[0], KBEInt32)
        assert values == [1, 2, 3, 4]

    def test_decode_of_unicode(self):
        decoder = UNICODE_ARRAY
        data = memoryview(
            b"\x03\x00\x00\x00\x01\x00\x00\x000\x02\x00\x00\x0012\x03\x00\x00\x00345"
        )
        value, offset = decoder.decode(data)
        assert offset == 22
        assert isinstance(value, KBEArray)
        assert value == ["0", "12", "345"]
        assert isinstance(value[0], KBEUnicode)

    def test_decode_of_empty_unicode(self):
        decoder = UNICODE_ARRAY
        data = memoryview(b"\x00\x00\x00\x00")
        value, offset = decoder.decode(data)
        assert offset == 4
        assert isinstance(value, KBEArray)
        assert value == []

    def test_decode_of_empty_string(self):
        decoder = STRING_ARRAY
        data = memoryview(b"\x00\x00\x00\x00")
        value, offset = decoder.decode(data)
        assert offset != 0
        assert isinstance(value, KBEArray)
        assert value == []

    def test_decode_of_string(self):
        decoder = STRING_ARRAY
        data = memoryview(b"\x03\x00\x00\x000\x0012\x00345\x00")
        value, offset = decoder.decode(data)
        assert offset == 13
        assert isinstance(value, KBEArray)
        assert value == ["0", "12", "345"]


class ArrayTestCase(unittest.TestCase):
    def setUp(self):
        self._arr: KBEArray[KBEUInt32] = KBEArray(
            [KBEUInt32(1), KBEUInt32(2), KBEUInt32(3)]
        )

    def test_get(self):
        assert self._arr[1] == 2

    def test_set(self):
        self._arr[1] = KBEUInt32(0)
        assert self._arr[1] == 0

    @pytest.mark.skip("Not implemented yet")
    def test_set_invalid_type(self):
        with pytest.raises(TypeError):
            self._arr[1] = "123"

    def test_extend(self):
        old_arr = self._arr
        self._arr.extend([KBEUInt32(10)])
        assert self._arr[-1] == 10
        assert self._arr == [1, 2, 3, 10]
        # It's the same object
        assert old_arr is self._arr

    @pytest.mark.skip("Not implemented yet")
    def test_extend_invalid_type(self):
        old_arr = self._arr
        with pytest.raises(TypeError):
            self._arr.extend(["10"])

        assert self._arr == [1, 2, 3]
        # It's the same object
        assert old_arr is self._arr


class ArrayOfFixedDictTestCase(unittest.TestCase):
    """Tests for array of fixed dicts."""

    def test_array_of_fd(self):
        """Test of empty array decoding."""

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

        class AVATAR_INFO(
            FIXED_DICT[AvatarInfoFixedDict, AvatarInfoFixedDictDecoders]
        ):
            _result_type = AvatarInfoFixedDict
            _decoders = AvatarInfoFixedDictDecoders

        class STRING_ARRAY(ARRAY[AvatarInfoFixedDict, AVATAR_INFO]):
            _element_decoder = AVATAR_INFO

        decoder = STRING_ARRAY
        data = memoryview(
            b"\x01\x00\x00\x00\x06\x00\x00\x00QWERTY\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00"
        )
        value, offset = decoder.decode(data)
        assert offset == 26
        assert isinstance(value, KBEArray)
        assert len(value) == 1
        assert isinstance(value[0], KBEFixedDict)
        assert dict(dataclasses.asdict(value[0])) == {
            "name": "QWERTY",
            "uid": 1,
            "dbid": 2,
        }
