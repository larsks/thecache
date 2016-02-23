import os
import unittest
import itertools
import tempfile

from io import BytesIO

from thecache.cache import Cache

from io import BytesIO

sample_data_1 = 'sample\ndata\n'
sample_data_2 = ''.join(chr(x) for x in range(254))


def chunker(data, chunksize=2):
    return [''.join(x) for x in itertools.izip_longest(
            *[iter(data)]*chunksize)]


class TestCache(unittest.TestCase):
    def setUp(self):
        self.cachedir = tempfile.mkdtemp()
        self.cache = Cache(__name__,
                           cachedir=self.cachedir)
        self.cache.invalidate_all()

    def tearDown(self):
        self.cache.invalidate_all()
        for dirpath, dirnames, filenames in os.walk(
                self.cachedir, topdown=False):
            for name in dirnames:
                os.rmdir(os.path.join(dirpath, name))

        os.rmdir(self.cachedir)

    def test_has(self):
        self.cache.store('testkey1', sample_data_1)
        self.assertTrue(self.cache.has('testkey1'))

    def tearDown(self):
        self.cache.invalidate_all()

    def test_has(self):
        self.cache.store('testkey1', sample_data_1)
        self.assertTrue(self.cache.has('testkey1'))

    def test_simple(self):
        self.cache.store('testkey1', sample_data_1)
        val = self.cache.load('testkey1')
        self.assertEqual(val, sample_data_1)

    def test_store_lines(self):
        self.cache.store_lines('testkey1',
                               sample_data_1.splitlines())
        val = list(self.cache.load_lines('testkey1'))
        self.assertEqual(val, ['sample', 'data'])

    def test_read_lines(self):
        self.cache.store('testkey1', sample_data_1)
        val = list(self.cache.load_lines('testkey1'))
        self.assertEqual(val, ['sample', 'data'])

    def test_store_chunks(self):
        self.cache.store_iter('testkey2', chunker(sample_data_2))
        val = self.cache.load('testkey2')

        self.assertEqual(sample_data_2, val)

    def test_read_chunks(self):
        self.cache.store_iter('testkey2', sample_data_2)
        acc = []
        for data in self.cache.load_iter('testkey2'):
            acc.append(data)

        val = ''.join(acc)
        self.assertEqual(sample_data_2, val)

    def test_missing(self):
        with self.assertRaises(KeyError):
            self.cache.load('testkey1')

    def test_delete(self):
        self.cache.store('testkey1', sample_data_1)
        val = self.cache.load('testkey1')
        self.assertEqual(val, sample_data_1)

        self.cache.invalidate('testkey1')
        with self.assertRaises(KeyError):
            val = self.cache.load('testkey1')

    def test_store_fd(self):
        fd = BytesIO(sample_data_2)
        self.cache.store_fd('testkey2', fd)
        val = self.cache.load('testkey2')
        self.assertEqual(val, sample_data_2)

    def test_load_fd(self):
        self.cache.store('testkey2', sample_data_2)
        fd = self.cache.load_fd('testkey2')
        val = fd.read()
        self.assertEqual(val, sample_data_2)

    def test_invalidate_missing(self):
        self.cache.invalidate('key that does not exist')

    def test_expire(self):
        self.cache = Cache(__name__, lifetime=0)
        self.cache.store('testkey1', sample_data_1)
        with self.assertRaises(KeyError):
            self.cache.load('testkey1')

    def test_noexpire(self):
        self.cache = Cache(__name__, lifetime=0)
        self.cache.store('testkey1', sample_data_1)
        val = self.cache.load('testkey1', noexpire=True)
        self.assertEqual(val, sample_data_1)
