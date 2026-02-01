"""Tests of FixedDict encoder / decoder."""

import collections
import unittest

import pytest


@pytest.mark.skip("Not implemented yet")
class ArrayTypeTestCase(unittest.TestCase):
    """Tests for Array."""

    def setUp(self):
        super().setUp()

    def test_decode_empty(self):
        """Test of empty array decoding."""
        self._decoder = ARRAY.build("INT_ARRAY", INT32)
        data = memoryview(b"\x00\x00\x00\x00")
        value, offset = self._decoder.decode(data)
        assert offset != 0
        assert isinstance(value, Array)
        assert value == []

    def test_decode_of_int(self):
        """Test FD decoding."""
        self._decoder = ARRAY.build("INT_ARRAY", INT32)
        data = memoryview(
            b"\x04\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00"
        )
        value, offset = self._decoder.decode(data)
        assert offset == 20
        assert isinstance(value, Array)
        assert len(value) == 4  # three keys
        assert value == [1, 2, 3, 4]

    def test_decode_of_unicode(self):
        self._decoder = ARRAY.build("UNICODE_ARRAY", UNICODE)
        data = memoryview(
            b"\x03\x00\x00\x00\x01\x00\x00\x000\x02\x00\x00\x0012\x03\x00\x00\x00345"
        )
        value, offset = self._decoder.decode(data)
        assert offset == 22
        assert isinstance(value, Array)
        assert value == ["0", "12", "345"]

    def test_decode_of_empty_unicode(self):
        self._decoder = ARRAY.build("UNICODE_ARRAY", UNICODE)
        data = memoryview(b"\x00\x00\x00\x00")
        value, offset = self._decoder.decode(data)
        assert offset == 4
        assert isinstance(value, Array)
        assert value == []

    def test_decode_of_empty_string(self):
        self._decoder = ARRAY.build("STRING_ARRAY", STRING)
        data = memoryview(b"\x00\x00\x00\x00")
        value, offset = self._decoder.decode(data)
        assert offset != 0
        assert isinstance(value, Array)
        assert value == []

    def test_decode_of_string(self):
        self._decoder = ARRAY.build("STRING_ARRAY", STRING)
        data = memoryview(b"\x03\x00\x00\x000\x0012\x00345\x00")
        value, offset = self._decoder.decode(data)
        assert offset == 13
        assert isinstance(value, Array)
        assert value == ["0", "12", "345"]


@pytest.mark.skip("Not implemented yet")
class ArrayTestCase(unittest.TestCase):
    def setUp(self):
        self._arr = Array(
            of=int, type_name="UNITTEST_ARRAY", initial_data=[1, 2, 3]
        )

    def test_get(self):
        assert self._arr[1] == 2

    def test_set(self):
        self._arr[1] = 0
        assert self._arr[1] == 0

    def test_set_invalid_type(self):
        with pytest.raises(TypeError):
            self._arr[1] = "123"

    def test_extend(self):
        old_arr = self._arr
        self._arr.extend([10])
        assert self._arr[-1] == 10
        assert self._arr == [1, 2, 3, 10]
        # It's the same object
        assert old_arr is self._arr

    def test_extend_invalid_type(self):
        old_arr = self._arr
        with pytest.raises(TypeError):
            self._arr.extend(["10"])

        assert self._arr == [1, 2, 3]
        # It's the same object
        assert old_arr is self._arr


@pytest.mark.skip("Not implemented yet")
class ArrayOfFixedDictTestCase(unittest.TestCase):
    """Tests for array of fixed dicts."""

    def test_array_of_fd(self):
        """Test of empty array decoding."""
        fd_decoder = FIXED_DICT.build(
            "AVATAR_INFO",
            collections.OrderedDict(
                [
                    ("name", UNICODE.create_alias("AVATAR_NAME")),
                    ("uid", INT32.create_alias("AVATAR_UID")),
                    ("dbid", UINT64.create_alias("DBID")),
                ]
            ),
        )
        self._decoder = ARRAY.build("AVATAR_INFO_LIST", fd_decoder)
        data = memoryview(
            b"\x01\x00\x00\x00\x06\x00\x00\x00QWERTY\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00"
        )
        value, offset = self._decoder.decode(data)
        assert offset == 26
        assert isinstance(value, Array)
        assert len(value) == 1
        assert isinstance(value[0], FixedDict)
        assert dict(value[0]) == {"name": "QWERTY", "uid": 1, "dbid": 2}
