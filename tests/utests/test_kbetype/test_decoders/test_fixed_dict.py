"""Tests of FixedDict encoder / decoder."""

import collections
import unittest

import pytest


@pytest.mark.skip("Not implemented yet")
class FixedDictTypeEmptyTestCase(unittest.TestCase):
    """Tests for FixedDict."""

    def setUp(self):
        super().setUp()
        # the real value from KBEngine

        self._fixed_dict = FIXED_DICT.build(
            "AVATAR_INFO",
            collections.OrderedDict(
                [("name", UNICODE), ("uid", INT32), ("dbid", UINT64)]
            ),
        )

    def test_decode_empty(self):
        """Test empty FD decoding."""
        data = memoryview(
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        )
        value, offset = self._fixed_dict.decode(data)
        assert offset != 0
        assert isinstance(value, FixedDict)
        assert len(value) == 3  # three keys
        assert value == {"name": "", "uid": 0, "dbid": 0}

    def test_decode(self):
        """Test FD decoding."""
        data = memoryview(
            b"\x06\x00\x00\x00QWERTY\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00"
        )
        value, offset = self._fixed_dict.decode(data)
        assert offset != 0
        assert isinstance(value, FixedDict)
        assert len(value) == 3  # three keys
        assert value == {"name": "QWERTY", "uid": 1, "dbid": 2}


@pytest.mark.skip("Not implemented yet")
class FixedDictInitTestCase(unittest.TestCase):
    """Initialization of FixedDict."""

    def setUp(self):
        super().setUp()

    def test_negative_no_args(self):
        with pytest.raises(TypeError):
            FixedDict()

    def test_init(self):
        fd = FixedDict(
            "UNITTEST_TYPE", collections.OrderedDict([("x", 0), ("y", 0)])
        )
        assert fd._data == collections.OrderedDict([("x", 0), ("y", 0)])

    def test_fd_is_plugin_type(self):
        """FixedDict should be a plugin type."""
        FixedDict(
            "UNITTEST_TYPE", collections.OrderedDict([("x", 0), ("y", 0)])
        )
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
            collections.OrderedDict(
                [("name", "name"), ("uid", 123), ("dbid", 56)]
            ),
        )
        fd["uid"] = 0
        assert fd._data == collections.OrderedDict(
            [("name", "name"), ("uid", 0), ("dbid", 56)]
        )

    def test_negative_invalid_value_type(self):
        fd = FixedDict(
            "UNITTEST_TYPE",
            collections.OrderedDict(
                [("name", "name"), ("uid", 123), ("dbid", 56)]
            ),
        )
        with pytest.raises(KeyError):
            fd["uid"] = "string"
        # Values is the same
        assert fd._data == collections.OrderedDict(
            [("name", "name"), ("uid", 123), ("dbid", 56)]
        )
