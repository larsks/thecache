from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import six
import tempfile
import unittest

from io import BytesIO

from thecache.cache import Cache

sample_data_1 = six.b('sample\ndata\n')
sample_data_2 = b''.join(six.int2byte(x) for x in range(254))


def chunker(data, chunksize=2):
    return (data[i:i+chunksize]
            for i in range(0, len(data), chunksize))


class TestCache(unittest.TestCase):
    def get_cache(self, lifetime=None):
        return Cache(__name__,
                     cachedir=self.cachedir,
                     lifetime=lifetime)

    def setUp(self):
        self.cachedir = tempfile.mkdtemp()

    def tearDown(self):
        for dirpath, dirnames, filenames in os.walk(
                self.cachedir, topdown=False):
            for name in filenames:
                os.unlink(os.path.join(dirpath, name))
            for name in dirnames:
                os.rmdir(os.path.join(dirpath, name))

        os.rmdir(self.cachedir)

    def test_has(self):
        cache = self.get_cache()
        cache.store('testkey1', sample_data_1)
        self.assertTrue(cache.has('testkey1'))

    def test_simple(self):
        cache = self.get_cache()
        cache.store('testkey1', sample_data_1)
        val = cache.load('testkey1')
        self.assertEqual(val, sample_data_1)

    def test_store_lines(self):
        cache = self.get_cache()
        cache.store_lines('testkey1',
                          sample_data_1.splitlines())
        val = list(cache.load_lines('testkey1'))
        self.assertEqual(val, [b'sample', b'data'])

    def test_read_lines(self):
        cache = self.get_cache()
        cache.store('testkey1', sample_data_1)
        val = list(cache.load_lines('testkey1'))
        self.assertEqual(val, [b'sample', b'data'])

    def test_store_chunks(self):
        cache = self.get_cache()
        cache.store_iter('testkey2', chunker(sample_data_2))
        val = cache.load('testkey2')

        self.assertEqual(sample_data_2, val)

    def test_read_chunks(self):
        cache = self.get_cache()
        cache.store_iter('testkey2',
                         chunker(sample_data_2))
        acc = []
        for data in cache.load_iter('testkey2'):
            acc.append(data)

        val = b''.join(acc)
        self.assertEqual(sample_data_2, val)

    def test_missing(self):
        cache = self.get_cache()
        with self.assertRaises(KeyError):
            cache.load('testkey1')

    def test_delete(self):
        cache = self.get_cache()
        cache.store('testkey1', sample_data_1)
        val = cache.load('testkey1')
        self.assertEqual(val, sample_data_1)

        cache.invalidate('testkey1')
        with self.assertRaises(KeyError):
            val = cache.load('testkey1')

    def test_store_fd(self):
        cache = self.get_cache()
        fd = BytesIO(sample_data_2)
        cache.store_fd('testkey2', fd)
        val = cache.load('testkey2')
        self.assertEqual(val, sample_data_2)

    def test_load_fd(self):
        cache = self.get_cache()
        cache.store('testkey2', sample_data_2)
        fd = cache.load_fd('testkey2')
        val = fd.read()
        self.assertEqual(val, sample_data_2)

    def test_invalidate_missing(self):
        cache = self.get_cache()
        cache.invalidate('key that does not exist')

    def test_expire(self):
        cache = self.get_cache(lifetime=0)
        cache.store('testkey1', sample_data_1)
        with self.assertRaises(KeyError):
            cache.load('testkey1')

    def test_noexpire(self):
        cache = self.get_cache(lifetime=0)
        cache.store('testkey1', sample_data_1)
        val = cache.load('testkey1', noexpire=True)
        self.assertEqual(val, sample_data_1)
