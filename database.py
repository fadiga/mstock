#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Autor: Fadiga

from Common.models import (Organization, License,
                           SettingsAdmin, Version, FileJoin)
from models import (Owner, Category, Store,
                    Product, Reports, Invoice, InvoiceItem)


def setup(drop_tables=False):
    """ create tables if not exist """

    did_create = False

    for model in [SettingsAdmin, Version, FileJoin, License,
                  Organization, Store, Product, Category, Reports,
                  Owner, Invoice, InvoiceItem]:
        if drop_tables:
            model.drop_table()
        if not model.table_exists():
            model.create_table()
            did_create = True
    if did_create:
        from fixture import fixt_init
        fixt_init().creat_all_or_pass()

setup()
