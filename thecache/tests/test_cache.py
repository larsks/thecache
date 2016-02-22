from thecache.cache import Cache
import unittest
import itertools

sample_data_1 = 'sample\ndata\n'
sample_data_2 = ''.join(chr(x) for x in range(254))


def chunker(data, chunksize=2):
    return [''.join(x) for x in itertools.izip_longest(
            *[iter(data)]*chunksize)]


class TestCache(unittest.TestCase):
    def setUp(self):
        self.cache = Cache(__name__)
        self.cache.invalidate_all()

    def test_simple(self):
        self.cache.store('testkey1', sample_data_1)
        val = self.cache.load('testkey1')
        self.assertEqual(val, sample_data_1)

    def test_lines(self):
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
