#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga

import os

from distutils.core import setup
import py2exe
import peewee

try:
    target = os.environ['PY2EXE_MODE']
except KeyError:
    target = 'multi'

if target == 'single':
    ZIPFILE = None
    BUNDLES = 1
else:
    ZIPFILE = 'shared.lib'
    BUNDLES = 1

includes = ['sip']
packages = ['sqlalchemy.dialects.sqlite']

setup(windows=[{'script': 'main_gdoug.py', \
                'icon_resources': [(0, 'images\\star.ico')]}],
      options={'py2exe': {
                    'includes': includes,
                    'packages': packages,
                    'compressed': True,
                    'bundle_files': BUNDLES,
                    },
               },
      zipfile=ZIPFILE,
)
