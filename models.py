#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from datetime import datetime

from Common import peewee
from GCommon.models import (BaseModel, SettingsAdmin, Version, FileJoin, Organization,
                            Owner, Category, Store)


class Store(Store):

    def last_report(self):
        return self.get_or_none(Reports.select().where(Reports.store == self).order_by(Reports.date.desc()))

    def lasts_reports(self):
        try:
            return Reports.select().where(Reports.store == self).order_by(Reports.date.desc()).all()
        except Exception as e:
            # print("lasts_reports ", e)
            raise

    def get_reports(self):

        try:
            return Reports.select().where(Reports.store == self)
        except Common.peewee.ReportsDoesNotExist as e:
            print("get_reports ", e)

    def get_report_or_none(self):
        return self.get_or_none(Reports.select().where(Reports.store == self))

    def get_remaining_and_nb_parts(self, prod):

        remaining = 0

        rpt = self.get_or_none(
            self.get_reports()
                  .where(Reports.product == prod)
                  .order_by(Reports.date.desc()))
        if rpt:
            remaining = rpt.remaining
            # print(rpt.product.name)
        return remaining, prod.number_parts_box


class Category(Category):

    def all_prod(self):
        return Product.select().where(Product.category == self)


class Product(BaseModel):

    # class Meta:
    #     ordering = (('name', 'desc'))

    date = peewee.DateTimeField(default=datetime.now())
    code = peewee.CharField(max_length=30, unique=True, null=True)
    name = peewee.CharField(max_length=50, unique=True)
    number_parts_box = peewee.IntegerField(default=1)
    category = peewee.ForeignKeyField(
        Category, related_name='category_products')
    file_join = peewee.ForeignKeyField(
        FileJoin, null=True, related_name='file_joins_products')

    def __str__(self):
        return self.name

    def save(self):
        self.code = self.code if self.code else self.name.lower().replace(
            " ", "")
        super(Product, self).save()

    def display_name(self):
        return u"{}".format(self.name)

    def get_report_or_none(self):
        return self.get_or_none(Reports.select().where(Reports.product == self))

    @property
    def image_link(self):
        try:
            return self.file_join.get_file
        except Exception as e:
            return None

    @property
    def last_report(self):
        try:
            last = report.order_by(Reports.date.desc()).get()
        except Exception as e:
            last = None
        return last

    def reports(self):
        try:
            return report.order_by(Reports.date.desc())
        except Exception as e:
            # print(e)
            pass

    @property
    def report(self):
        return Reports.select().where(Reports.product == self)


class Reports(BaseModel):

    """ """

    E = "e"
    S = "s"
    TYPES = ((E, "Entrée"), (S, "Sortie"))

    type_ = peewee.CharField(choices=TYPES, default=E)
    store = peewee.ForeignKeyField(Store, related_name='store_reports')
    product = peewee.ForeignKeyField(Product, related_name='product_reports')
    qty_use = peewee.IntegerField(default=0)
    remaining = peewee.IntegerField(default=0)
    date = peewee.DateTimeField(default=datetime.now())
    registered_on = datetime.now()
    deleted = peewee.BooleanField(default=False)

    def __str__(self):
        return u"{product} --> {store} le {type_} \
                 {.date}".format(type_=self.type_,
                                 date=self.date.strftime('%x %Hh:%Mmm'),
                                 store=self.store,
                                 product=self.product)

    def save(self):
        """
        Calcul du remaining en stock après une operation."""
        from Common.ui.util import raise_error
        # print("SAVE BEGIN")
        try:
            try:
                last_reports = self.last_report()
                # print("LAST REPORT: ", last_reports)
                previous_remaining = last_reports.remaining
                # print("previous_remaining: ", previous_remaining)
            except Exception as e:
                # print("last_reports", e)
                previous_remaining = 0
            if self.type_ == self.E:
                self.remaining = int(previous_remaining) + int(self.qty_use)
            if self.type_ == self.S:
                self.remaining = int(previous_remaining) - int(self.qty_use)
                if self.remaining < 0:
                    raise_error(u"Erreur",
                                u"On peut pas utilisé %d puis qu'il ne reste que %d"
                                % (self.qty_use, previous_remaining))
                    return False
        except Exception as e:
            # print(e)
            if self.type_ == self.S:
                raise_error(u"Erreur",
                            u"Il n'existe aucun %s dans le store %s"
                            % (self.product.name, self.store.name))
                return False

        super(Reports, self).save()
        try:
            next_rpts = self.report.order_by(Reports.date.asc())
            next_rpt = next_rpts.get()
            next_rpt.save()
        except Exception as e:
            # print("next_rpt", e)
            pass
    # 793O5759

    def last_report(self):
        try:
            return self.report.order_by(Reports.date.desc()).get()
        except Exception as e:
            # print("last_report", e)
            return None

    @property
    def report(self):
        return Reports.select().where(Reports.product == self.product,
                                      Reports.store == self.store,
                                      Reports.date < self.date,
                                      Reports.deleted == False)


class Invoice(BaseModel):

    """ Represents an order
    """

    TYPE_FACT = 'f'
    TYPE_PROF = 'p'
    TYPES = (
        (TYPE_FACT, u"Facture"),
        (TYPE_PROF, u"Proforma")
    )
    owner = peewee.ForeignKeyField(Owner, verbose_name=("Proprietaire"))
    number = peewee.IntegerField(verbose_name=("Numero"), unique=True)
    date = peewee.DateTimeField(verbose_name=("Fait le"), default=datetime.now)
    client = peewee.CharField(max_length=30, verbose_name=("Doit"))
    location = peewee.CharField(max_length=50, null=True, verbose_name=("A"))
    type_ = peewee.CharField(max_length=30, choices=TYPES, default=TYPE_PROF)
    subject = peewee.CharField(
        max_length=100, null=True, verbose_name=("Objet"))
    tax = peewee.BooleanField(default=False)
    tax_rate = peewee.IntegerField(null=True, verbose_name=("Taux"),
                                   default=18)

    def __str__(self):
        return "{num}/{client}/{owner}".format(num=self.number, owner=self.owner,
                                               client=self.client)

    @classmethod
    def get_next_number(cls, org):
        """ Get a valid number automatically incremented from
            the higher one.
        """
        number = 1
        if Invoice.select().count():
            number += int(Invoice.latest('number').number)
        return number

    @property
    def items(self):
        try:
            return InvoiceItem.select().where(InvoiceItem.invoices == self)
        except Exception as e:
            print("Invoice", e)

    # @property
    # def date(self):
    #     return self.items.first().date

    def display_name(self):
        return u"Facture N: {num} de {client} au {date}".format(num=self.number,
                                                                client=self.client, date=self.date.strftime("%c"))


class InvoiceItem(BaseModel):

    """ Represents an element of an order such as a product
    """
    description = peewee.ForeignKeyField(Product, verbose_name=("Description"))
    quantity = peewee.IntegerField(verbose_name=("Quantite"))
    price = peewee.IntegerField(verbose_name=("Prix"))
    invoices = peewee.ForeignKeyField(Invoice)

    def __str__(self):
        return u"{desc} {qty} {price}".format(qty=self.quantity,
                                              desc=self.description,
                                              price=self.price)
