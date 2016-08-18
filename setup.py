#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Christian Karrié <christian@karrie.info>'

from distutils.core import setup

# Dynamically calculate the version based on ccm.VERSION
version_tuple = __import__('tvhm').VERSION
version = ".".join([str(v) for v in version_tuple])

setup(
    name = 'django-tvhmanager',
    description = 'TVHeadend Manager',
    version = version,
    author = 'Christian Karrie',
    author_email = 'ckarrie@gmail.com',
    url = 'http://ccm.app/',
    packages=['tvhm'],
)

