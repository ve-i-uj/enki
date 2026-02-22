"""Tests of FixedDict encoder / decoder."""

import copy
import dataclasses
from dataclasses import dataclass
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
    _kbe_type = AvatarInfoFixedDict
    _decoders = AvatarInfoFixedDictDecoders


class AVATAR_INFO_ARRAY(ARRAY[AvatarInfoFixedDict, AVATAR_INFO]):
    _element_decoder = AVATAR_INFO


@dataclass
class SimpleFixedDict(KBEFixedDict):
    field1: KBEUnicode
    field2: KBEInt32


@dataclass
class SimpleFixedDictDecoders(FixedDictDecoders):
    field1: type[UNICODE] = UNICODE
    field2: type[INT32] = INT32


class SIMPLE_FD(FIXED_DICT[SimpleFixedDict, SimpleFixedDictDecoders]):
    _kbe_type = SimpleFixedDict
    _decoders = SimpleFixedDictDecoders


class INT32_ARRAY(ARRAY[KBEInt32, INT32]):
    """Декодер для типа массива INT."""

    _element_decoder = INT32
    _kbe_type = KBEArray[KBEInt32]

    @classmethod
    def get_kbe_type(cls) -> type[KBEArray[KBEInt32]]:
        return cls._kbe_type

    @classmethod
    def _get_element_decoder(cls) -> type[INT32]:
        return INT32


class UNICODE_ARRAY(ARRAY[KBEUnicode, UNICODE]):
    """Декодер для типа массива UNICODE."""

    _element_decoder = UNICODE


class STRING_ARRAY(ARRAY[KBEUnicode, STRING]):
    """Декодер для типа массива STRING."""

    _element_decoder = STRING


class Test_ARRAY:
    """Tests for KBEArray."""

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

    # Тесты для encode
    def test_encode_empty_int32_array(self):
        """Test encoding empty INT32 array."""
        arr = KBEArray([])
        encoded = INT32_ARRAY.encode(arr)
        assert encoded == b"\x00\x00\x00\x00"

    def test_encode_int32_array(self):
        """Test encoding INT32 array with values."""
        arr = KBEArray([KBEInt32(1), KBEInt32(2), KBEInt32(3), KBEInt32(4)])
        encoded = INT32_ARRAY.encode(arr)
        expected = (
            b"\x04\x00\x00\x00"  # длина массива = 4
            b"\x01\x00\x00\x00"  # 1
            b"\x02\x00\x00\x00"  # 2
            b"\x03\x00\x00\x00"  # 3
            b"\x04\x00\x00\x00"  # 4
        )
        assert encoded == expected

    def test_encode_decode_roundtrip_int32(self):
        """Test that encode/decode are inverses for INT32 array."""
        original = KBEArray(
            [
                KBEInt32(10),
                KBEInt32(20),
                KBEInt32(30),
                KBEInt32(40),
                KBEInt32(50),
            ]
        )

        encoded = INT32_ARRAY.encode(original)
        decoded, offset = INT32_ARRAY.decode(memoryview(encoded))

        assert offset == len(encoded)
        assert decoded == original
        for i in range(len(original)):
            assert decoded[i] == original[i]
            assert isinstance(decoded[i], KBEInt32)

    def test_encode_unicode_array(self):
        """Test encoding UNICODE array."""
        arr = KBEArray(
            [KBEUnicode("test"), KBEUnicode("hello"), KBEUnicode("world")]
        )
        encoded = UNICODE_ARRAY.encode(arr)

        expected = (
            b"\x03\x00\x00\x00"  # длина массива = 3
            b"\x04\x00\x00\x00test"  # "test" (4 байта)
            b"\x05\x00\x00\x00hello"  # "hello" (5 байт)
            b"\x05\x00\x00\x00world"  # "world" (5 байт)
        )
        assert encoded == expected

    def test_encode_string_array(self):
        """Test encoding STRING array."""
        arr = KBEArray([KBEUnicode("a"), KBEUnicode("bc"), KBEUnicode("def")])
        encoded = STRING_ARRAY.encode(arr)

        expected = (
            b"\x03\x00\x00\x00"  # длина массива = 3
            b"a\x00"  # "a" + нулевой байт
            b"bc\x00"  # "bc" + нулевой байт
            b"def\x00"  # "def" + нулевой байт
        )
        assert encoded == expected

    def test_encode_array_with_special_characters(self):
        """Test encoding array with special characters."""
        arr = KBEArray(
            [KBEUnicode("тест"), KBEUnicode("😀"), KBEUnicode("line\nbreak")]
        )

        encoded = UNICODE_ARRAY.encode(arr)
        decoded, _ = UNICODE_ARRAY.decode(memoryview(encoded))

        assert decoded == ["тест", "😀", "line\nbreak"]

    def test_encode_array_max_length(self):
        """Test encoding array with max values."""
        arr = KBEArray([KBEInt32(2**31 - 1)] * 100)
        encoded = INT32_ARRAY.encode(arr)

        decoded, offset = INT32_ARRAY.decode(memoryview(encoded))
        assert offset == len(encoded)
        assert len(decoded) == 100
        assert all(val == 2**31 - 1 for val in decoded)


class TestArrayMethods:
    _arr: KBEArray[KBEUInt32] = KBEArray(
        [KBEUInt32(1), KBEUInt32(2), KBEUInt32(3)]
    )

    def test_get(self):
        assert self._arr[1] == 2

    def test_set(self):
        arr = copy.deepcopy(self._arr)
        arr[1] = KBEUInt32(0)
        assert arr[1] == 0

    @pytest.mark.skip("Not implemented yet")
    def test_set_invalid_type(self):
        arr = copy.deepcopy(self._arr)
        with pytest.raises(TypeError):
            arr[1] = "123"  # type: ignore

    def test_extend(self):
        arr = copy.deepcopy(self._arr)
        arr.extend([KBEUInt32(10)])
        assert arr[-1] == 10
        assert arr == [1, 2, 3, 10]

    @pytest.mark.skip("Not implemented yet")
    def test_extend_invalid_type(self):
        arr = copy.deepcopy(self._arr)
        with pytest.raises(TypeError):
            arr.extend(["10"])  # type: ignore

        assert arr == [1, 2, 3]


class TestArrayOfFixedDict:
    """Tests for array of fixed dicts."""

    def test_array_of_fd(self):
        """Test of empty array decoding."""
        decoder = AVATAR_INFO_ARRAY
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

    def test_encode_array_of_fixed_dict(self):
        """Test encoding array of FixedDict."""
        arr = KBEArray(
            [
                AvatarInfoFixedDict(
                    name=KBEUnicode("User1"),
                    uid=KBEInt32(100),
                    dbid=KBEDbid(1000),
                ),
                AvatarInfoFixedDict(
                    name=KBEUnicode("User2"),
                    uid=KBEInt32(200),
                    dbid=KBEDbid(2000),
                ),
            ]
        )

        encoded = AVATAR_INFO_ARRAY.encode(arr)

        expected = (
            b"\x02\x00\x00\x00"  # длина массива = 2
            # Первый элемент
            b"\x05\x00\x00\x00User1"  # name: "User1"
            b"\x64\x00\x00\x00"  # uid: 100
            b"\xe8\x03\x00\x00\x00\x00\x00\x00"  # dbid: 1000
            # Второй элемент
            b"\x05\x00\x00\x00User2"  # name: "User2"
            b"\xc8\x00\x00\x00"  # uid: 200
            b"\xd0\x07\x00\x00\x00\x00\x00\x00"  # dbid: 2000
        )

        assert encoded == expected

    def test_encode_decode_roundtrip_array_of_fd(self):
        """Test encode/decode roundtrip for array of FixedDict."""
        original = KBEArray(
            [
                AvatarInfoFixedDict(
                    name=KBEUnicode("Alice"), uid=KBEInt32(1), dbid=KBEDbid(100)
                ),
                AvatarInfoFixedDict(
                    name=KBEUnicode("Bob"), uid=KBEInt32(2), dbid=KBEDbid(200)
                ),
                AvatarInfoFixedDict(
                    name=KBEUnicode("Charlie"),
                    uid=KBEInt32(3),
                    dbid=KBEDbid(300),
                ),
            ]
        )

        encoded = AVATAR_INFO_ARRAY.encode(original)
        decoded, offset = AVATAR_INFO_ARRAY.decode(memoryview(encoded))

        assert offset == len(encoded)
        assert len(decoded) == 3

        for i in range(3):
            assert decoded[i].name == original[i].name
            assert decoded[i].uid == original[i].uid
            assert decoded[i].dbid == original[i].dbid


class TestFixedDictEncode:
    """Tests for FixedDict encoding."""

    def test_encode_simple_fixed_dict(self):
        """Test encoding simple FixedDict."""
        fd = SimpleFixedDict(field1=KBEUnicode("test"), field2=KBEInt32(42))

        encoded = SIMPLE_FD.encode(fd)

        expected = (
            b"\x04\x00\x00\x00test"  # field1: "test"
            b"\x2a\x00\x00\x00"  # field2: 42
        )
        assert encoded == expected

    def test_encode_fixed_dict_with_empty_string(self):
        """Test encoding FixedDict with empty string."""
        fd = SimpleFixedDict(field1=KBEUnicode(""), field2=KBEInt32(0))

        encoded = SIMPLE_FD.encode(fd)

        expected = (
            b"\x00\x00\x00\x00"  # field1: empty string
            b"\x00\x00\x00\x00"  # field2: 0
        )
        assert encoded == expected

    def test_encode_decode_roundtrip_fixed_dict(self):
        """Test encode/decode roundtrip for FixedDict."""
        original = SimpleFixedDict(
            field1=KBEUnicode("Hello, World!"), field2=KBEInt32(123456)
        )

        encoded = SIMPLE_FD.encode(original)
        decoded, offset = SIMPLE_FD.decode(memoryview(encoded))

        assert offset == len(encoded)
        assert decoded.field1 == original.field1
        assert decoded.field2 == original.field2

    def test_encode_fixed_dict_order(self):
        """Test that FixedDict encoding preserves field order."""
        fd = SimpleFixedDict(field1=KBEUnicode("first"), field2=KBEInt32(99))

        encoded = SIMPLE_FD.encode(fd)

        # Проверяем, что field1 идет первым (UNICODE декодер)
        # Длина строки "first" = 5
        assert encoded[:4] == b"\x05\x00\x00\x00"
        assert encoded[4:9] == b"first"
        # Затем field2 (INT32)
        assert encoded[9:] == b"\x63\x00\x00\x00"  # 99

    def test_encode_fixed_dict_nested_types(self):
        """Test encoding FixedDict with nested array type."""

        @dataclass
        class NestedFixedDict(KBEFixedDict):
            name: KBEUnicode
            scores: KBEArray[KBEInt32]

        @dataclass
        class NestedFixedDictDecoders(FixedDictDecoders):
            name: type[UNICODE] = UNICODE
            scores: type[INT32_ARRAY] = INT32_ARRAY

        class NESTED_FD(FIXED_DICT[NestedFixedDict, NestedFixedDictDecoders]):
            _kbe_type = NestedFixedDict
            _decoders = NestedFixedDictDecoders

        fd = NestedFixedDict(
            name=KBEUnicode("Player1"),
            scores=KBEArray([KBEInt32(100), KBEInt32(200), KBEInt32(300)]),
        )

        encoded = NESTED_FD.encode(fd)

        # Проверяем структуру
        assert encoded.startswith(b"\x07\x00\x00\x00Player1")
        # Далее должен идти массив из 3 элементов
        assert b"\x03\x00\x00\x00" in encoded
        assert b"\x64\x00\x00\x00" in encoded  # 100
        assert b"\xc8\x00\x00\x00" in encoded  # 200
        assert b"\x2c\x01\x00\x00" in encoded  # 300

        # Декодируем обратно для проверки
        decoded, _ = NESTED_FD.decode(memoryview(encoded))
        assert decoded.name == "Player1"
        assert decoded.scores == [100, 200, 300]
