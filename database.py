#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Autor: Fadiga

from models import (Category, Store,
                    Product, Reports, Invoice, InvoiceItem)


# def setup(drop_tables=False):
#     """ create tables if not exist """

#     did_create = False

#     for model in [SettingsAdmin, Version, FileJoin, License,
#                   Organization, Store, Product, Category, Reports,
#                   Owner, Invoice, InvoiceItem]:
#         if drop_tables:
#             model.drop_table()
#         if not model.table_exists():
#             model.create_table()
#             did_create = True
#     if did_create:
#         from fixture import FixtInit
#         FixtInit().create_all_or_pass()

# setup()

from Common.cdatabase import AdminDatabase


class Setup(AdminDatabase):

    """docstring for FixtInit"""

    def __init__(self):
        super(AdminDatabase, self).__init__()

        self.LIST_CREAT += [
            Category, Store, Product, Reports, Invoice, InvoiceItem]
        # self.LIST_CREAT.append(ProviderOrClient)
        self.CREATE_DB = False
