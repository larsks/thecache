[![travis-ci.org](https://travis-ci.org/larsks/thecache.svg)](https://travis-ci.org/larsks/thecache)
[![codecov.io](https://codecov.io/github/larsks/thecache/coverage.svg?branch=master)](https://codecov.io/github/larsks/thecache?branch=master)

This is a simple file-based cache implementation that is meant for
simple cases where you want to cache some data (maybe you want to
avoid hammering an API server with repeated requests) but you don't
want the features and associated configuration tasks associated with a
more feature-ful cache module.

## Usage

To get yourself a cache:

    >>> from thecache.cache import Cache
    >>> mycache = Cache(__name__)

To use the cache for small amounts of data (for memory efficient
operations, read the more detailed explanations below):

    >>> mycache.put('some key', 'a chunk of data')
    >>> if mycache.has('some key'):
    ...   print 'Content:', mycache.get('some key')
    ... else:
    ...   print 'Key "some key" was not in cache'
    ... 
    Content: a chunk of data

Or:

    >>> try:
    ...   print 'Content:', mycache.get('some key')
    ... except KeyError:
    ...   print 'Key "some key" was not in cache'
    ... 
    Content: a chunk of data

## Storing data

- `store` (also `put`)

  This will write the content of a Python variable to the cache.

- `store_fd`

  This will read from an open file in `chunksize` byte chunks and
  write the data to the cache.

- `store_iter`

  This will iterate over `content`, writing each chunk of data to the
  cache.  This is a good choice for handling a response from the
  `requests` library in streaming mode:

        >>> import requests
        >>> r = requests.get(url, stream=True)
        >>> c.store_iter(url, r.iter_content(chunk_size=8192))

- `store_lines`

  This is almost exactly like `store_iter`, except it appends a
  newline after writing each chunk of data.  This is useful for
  writing a list of strings to the cache to be read back using the
  `load_lines` method:

        >>> mydata = ['one', 'two', 'three', 'four']
        >>> c.store_lines('mykey', mydata)

## Reading data

All of the following functions raise `KeyError` if you request a key
that cannot be found in the cache.

- `load` (also `get`)

  This will read data from the cache into memory and return the data
  to the caller.

- `load_lines`

  This will return an iterator over the lines store in the cache.  The
  underlying file will be closed automatically when all lines have
  been read.

- `load_iter`

  This will return an iterator that yields data in `chunksize` byte
  chunks.  The underlying file will be closed automatically when all
  the data has been read.

- `load_fd`

  This will return an open file to the caller.  Is is the caller's job
  to close the file when it is no longer needed.

## Contributing

To report problems with this code, use the [issue tracker][].
Changes may be submitted as GitHub pull requests.

[issue tracker]: https://github.com/larsks/thecache/issues

Commits are verified using [travis-ci.org][travis], which
automatically runs `tox` after any pushes or pull requests.  You
should run `tox` locally to verify any changes before submitting them
to GitHub.

[travis]: http://travis-ci.org/

## License

thecache, a simple Python cache implementation  
Copyright (C) 2016 Lars Kellogg-Stedman <lars@oddbit.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


