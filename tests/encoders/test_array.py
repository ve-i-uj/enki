"""Tests of FixedDict encoder / decoder."""

import collections
import unittest

from enki import kbetype, interface


class ArrayTypeTestCase(unittest.TestCase):
    """Tests for Array"""

    def setUp(self):
        super().setUp()

    def test_decode_empty(self):
        """Test of empty array decoding."""
        self._decoder = kbetype.ARRAY.build('INT_ARRAY', kbetype.INT32)
        data = memoryview(b'\x00\x00\x00\x00')
        value, offset = self._decoder.decode(data)
        self.assertNotEqual(offset, 0)
        self.assertIsInstance(value, kbetype.Array)
        self.assertEqual(value, [])

    def test_decode_of_int(self):
        """Test FD decoding."""
        self._decoder = kbetype.ARRAY.build('INT_ARRAY', kbetype.INT32)
        data = memoryview(b'\x04\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00')
        value, offset = self._decoder.decode(data)
        self.assertEqual(offset, 20)
        self.assertIsInstance(value, kbetype.Array)
        self.assertEqual(len(value), 4)  # three keys
        self.assertEqual([1, 2, 3, 4], value)

    def test_decode_of_unicode(self):
        self._decoder = kbetype.ARRAY.build('UNICODE_ARRAY', kbetype.UNICODE)
        data = memoryview(b'\x03\x00\x00\x00\x01\x00\x00\x000\x02\x00\x00\x0012\x03\x00\x00\x00345')
        value, offset = self._decoder.decode(data)
        self.assertEqual(offset, 22)
        self.assertIsInstance(value, kbetype.Array)
        self.assertEqual(value, ['0', '12', '345'])

    def test_decode_of_empty_unicode(self):
        self._decoder = kbetype.ARRAY.build('UNICODE_ARRAY', kbetype.UNICODE)
        data = memoryview(b'\x00\x00\x00\x00')
        value, offset = self._decoder.decode(data)
        self.assertEqual(offset, 4)
        self.assertIsInstance(value, kbetype.Array)
        self.assertEqual(value, [])

    def test_decode_of_empty_string(self):
        self._decoder = kbetype.ARRAY.build('STRING_ARRAY', kbetype.STRING)
        data = memoryview(b'\x00\x00\x00\x00')
        value, offset = self._decoder.decode(data)
        self.assertNotEqual(offset, 0)
        self.assertIsInstance(value, kbetype.Array)
        self.assertEqual(value, [])

    def test_decode_of_string(self):
        self._decoder = kbetype.ARRAY.build('STRING_ARRAY', kbetype.STRING)
        data = memoryview(b'\x03\x00\x00\x000\x0012\x00345\x00')
        value, offset = self._decoder.decode(data)
        self.assertEqual(offset, 13)
        self.assertIsInstance(value, kbetype.Array)
        self.assertEqual(value, ['0', '12', '345'])


class ArrayTestCase(unittest.TestCase):

    def setUp(self):
        self._arr = kbetype.Array(of=int, type_name='UNITTEST_ARRAY',
                                  initial_data=[1, 2, 3])


    def test_get(self):
        self.assertEqual(2, self._arr[1])

    def test_set(self):
        self._arr[1] = 0
        self.assertEqual(0, self._arr[1])

    def test_set_invalid_type(self):
        with self.assertRaises(TypeError):
            self._arr[1] = '123'

    def test_extend(self):
        old_arr = self._arr
        self._arr.extend([10])
        self.assertEqual(10, self._arr[-1])
        self.assertEqual([1, 2, 3, 10], self._arr)
        # It's the same object
        self.assertIs(old_arr, self._arr)

    def test_extend_invalid_type(self):
        old_arr = self._arr
        with self.assertRaises(TypeError):
            self._arr.extend(['10'])

        self.assertEqual([1, 2, 3], self._arr)
        # It's the same object
        self.assertIs(old_arr, self._arr)
