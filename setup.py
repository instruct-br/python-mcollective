import sys
import setuptools
from setuptools.command import test

REQ = {'stomp.py>=4.0.10', 'six' }
TREQ = {
    'mock',
    'jinja2',
    'pytest',
    'pytest-xdist<1.9',
    'pytest-cov',
    'pyyaml',
    'pycrypto',
    'pytest-timeout',
} - REQ

try:
    import importlib  # noqa
except ImportError:
    REQ.add('importlib')

REQ = list(REQ)
TREQ = list(TREQ)

class PyTest(test.test):
    def finalize_options(self):
        test.test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setuptools.setup(
    cmdclass={'test': PyTest},
    name='python-mcollective',
    version='0.0.1.dev7',
    url='https://github.com/rafaduran/python-mcollective',
    author='Rafael Durán Castañeda',
    author_email='rafadurancastaneda@gmail.com',
    description=('Python bindings for MCollective'),
    license='BSD',
    packages=['pymco', 'pymco.connector', 'pymco.security',
        'pymco.serializers', 'pymco.test'],
    install_requires=REQ,
    extras_require={'ssl': ('pycrypto', 'PyYAML')},
    tests_require=TREQ,
    zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: System :: Systems Administration'
    ],
)
