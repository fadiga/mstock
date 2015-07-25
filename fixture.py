#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from __future__ import (unicode_literals, absolute_import, division, print_function)

import os, sys; sys.path.append(os.path.abspath('../'))

from Common.fixture import AdminFixture

from models import Owner, Store


class fixt_init(AdminFixture):
    """docstring for fixt_init"""
    def __init__(self):
        super(fixt_init, self).__init__()

        self.LIST_CREAT.append(Store(name=u"Magasin N°1", qte_maxi_stok=5000))

def passw(passw):
    return hashlib.sha224(passw).hexdigest()
