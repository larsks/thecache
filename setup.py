from setuptools import setup, find_packages
from thecache import __version__

with open('requirements.txt') as fd:
    requires = fd.read().splitlines()

setup(name='thecache',
      author='Lars Kellogg-Stedman',
      author_email='lars@oddbit.com',
      url='https://github.com/larsks/thecache',
      version=__version__,
      packages=find_packages(),
      install_requires=requires,
      test_suite='thecache.tests.test_cache',
      )
