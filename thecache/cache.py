import contextlib
import hashlib
import logging
import os
import pathlib2 as pathlib
import time

LOG = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = os.environ.get(
    'THE_CACHE_DIR', os.path.join(os.environ.get('HOME', ''),
                                  '.cache', 'the-cache'))

DEFAULT_CACHE_LIFETIME = 300
DEFAULT_CHUNK_SIZE = 8192


def line_iterator(fd):
    with contextlib.closing(fd) as fd:
        for line in fd:
            yield line.replace('\n', '').replace('\r', '')


def chunk_iterator(fd, chunksize=None):
    chunksize = chunksize or DEFAULT_CHUNK_SIZE

    with contextlib.closing(fd) as fd:
        while True:
            data = fd.read(chunksize)
            if not data:
                break

            yield data


@contextlib.contextmanager
def tempfile_writer(target):
    '''write cache data to a temporary location.  when writing is
    complete, rename the file to the actual location.  delete
    the temporary file on any error'''
    tmp = target.parent / ('_%s' % target.name)
    try:
        with tmp.open('wb') as fd:
            yield fd
    except:
        tmp.unlink()
        raise
    LOG.debug('rename %s -> %s', tmp, target)
    tmp.rename(target)


class Cache (object):
    def __init__(self, appid, cachedir=None, lifetime=None):
        # sanitize the appid
        appid = appid.replace('/', '_')

        self.cachedir = pathlib.Path(cachedir or DEFAULT_CACHE_DIR)
        self.appid = appid
        self.lifetime = (
            lifetime if lifetime is not None
            else DEFAULT_CACHE_LIFETIME)

        self.create_cache_dirs()

        LOG.debug('initialized cache with lifetime = %d',
                  self.lifetime)

    def get_app_cache(self):
        return pathlib.Path(self.cachedir, self.appid)

    def path(self, key):
        return pathlib.Path(
            self.get_app_cache(),
            key[:2],
            key)

    def has(self, key):
        path = self.path(self.xform_key(key))
        return path.exists()

    def create_cache_dirs(self):
        LOG.debug('creating cache directories')
        if not self.cachedir.is_dir():
            self.cachedir.mkdir(mode=0700)

        appcache = self.get_app_cache()
        if not appcache.is_dir():
            appcache.mkdir(mode=0700)

        for prefix in range(256):
            prefixdir = pathlib.Path(appcache, '{:02x}'.format(prefix))
            if not prefixdir.is_dir():
                prefixdir.mkdir(mode=0700)

    def xform_key(self, key):
        '''we transform cache keys by taking their sha1 hash so that
        we don't need to worry about cache keys containing invalid
        characters'''

        newkey = hashlib.sha1(key)
        return newkey.hexdigest()

    def invalidate(self, key):
        '''Clear an item from the cache'''
        path = self.path(self.xform_key(key))
        try:
            LOG.debug('invalidate %s (%s)', key, path)
            path.unlink()
        except OSError:
            pass

    def invalidate_all(self):
        '''Clear all items from the cache'''

        LOG.debug('clearing cache')
        appcache = str(self.get_app_cache())
        for dirpath, dirnames, filenames in os.walk(appcache):
            for name in filenames:
                try:
                    pathlib.Path(dirpath, name).unlink()
                except OSError:
                    pass

    def store_iter(self, key, content):
        '''stores content in the cache by iterating over
        content'''
        cachekey = self.xform_key(key)
        path = self.path(cachekey)

        with tempfile_writer(path) as fd:
            for data in content:
                LOG.debug('writing chunk of %d bytes for %s',
                          len(data), key)
                fd.write(data)
        LOG.debug('%s stored in cache', key)

    def store_lines(self, key, content):
        '''like store_iter, but appends a newline to each chunk of
        content'''
        return self.store_iter(
            key,
            (data + '\n' for data in content))

    def store_fd(self, key, content, chunksize=None):
        chunksize = chunksize or DEFAULT_CHUNK_SIZE
        cachekey = self.xform_key(key)
        path = self.path(cachekey)

        with tempfile_writer(path) as fd:
            while True:
                data = content.read(chunksize)
                if not data:
                    break
                fd.write(data)
        LOG.debug('%s stored in cache', key)

    def store(self, key, content):
        cachekey = self.xform_key(key)
        path = self.path(cachekey)

        with tempfile_writer(path) as fd:
            fd.write(content)
        LOG.debug('%s stored in cache', key)

    def load_fd(self, key, noexpire=False):
        '''Look up an item in the cache and return an open file
        descriptor for the object.  It is the caller's responsibility
        to close the file descriptor.'''

        cachekey = self.xform_key(key)
        path = self.path(cachekey)

        try:
            stat = path.stat()
            if not noexpire and stat.st_mtime < time.time() - self.lifetime:
                LOG.debug('%s has expired', key)
                path.unlink()
                raise KeyError(key)

            LOG.debug('%s found in cache', key)
            return path.open('rb')
        except OSError:
            LOG.debug('%s not found in cache', key)
            raise KeyError(key)

    def load_lines(self, key, noexpire=None):
        '''Look up up an item in the cache and return a line iterator.
        The underlying file will be closed once all lines have been
        consumed.'''
        return line_iterator(self.load_fd(key, noexpire=noexpire))

    def load_iter(self, key, chunksize=None, noexpire=None):
        '''Lookup an item in the cache and return an iterator
        that reads chunksize bytes of data at a time.  The underlying
        file will be closed when all data has been read'''
        return chunk_iterator(self.load_fd(key, noexpire=noexpire),
                              chunksize=chunksize)

    def load(self, key, noexpire=None):
        '''Lookup an item in the cache and return the raw content of
        the file as a string.'''
        with self.load_fd(key, noexpire=noexpire) as fd:
            return fd.read()

    put = store
    get = load
