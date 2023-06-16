#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import io
import os.path
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    with io.open(join(dirname(__file__), *names), encoding=kwargs.get('encoding', 'utf8')) as fh:
        return fh.read()


setup(
    name='iupred3-wrapper',
    version='0.2.1',
    license='MIT',
    description='Simple wrapper for iupred3 web interface.',
    long_description='{}'.format(
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.md'))
    ),
    long_description_content_type='text/markdown',
    author='Jakub J. Guzek',
    author_email='jakub.j.guzek@gmail.com',
    url='file://' + os.path.abspath(dirname(__file__)),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
        'Private :: Do Not Upload',
    ],
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires='>=3.10',
    install_requires=[
       "async-generator==1.10",
       "attrs==23.1.0",
       "biopython==1.81",
       "certifi==2023.5.7",
       "charset-normalizer==3.1.0",
       "exceptiongroup==1.1.1",
       "gevent==22.10.2",
       "greenlet==2.0.2",
       "grequests==0.7.0",
       "h11==0.14.0",
       "idna==3.4",
       "lxml==4.9.2",
       "numpy==1.24.3",
       "outcome==1.2.0",
       "PySocks==1.7.1",
       "requests==2.31.0",
       "selenium==4.10.0",
       "sniffio==1.3.0",
       "sortedcontainers==2.4.0",
       "trio==0.22.0",
       "trio-websocket==0.10.3",
       "urllib3==2.0.3",
       "wsproto==1.2.0",
       "zope.event==4.6",
       "zope.interface==6.0"
    ]
)
