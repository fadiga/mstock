#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga

from datetime import datetime
from models import Reports, Product, Store


def lastes_reports():
    list_rep = []
    for store in Store.select():
        for prod in Product.select():
            try:
                list_rep.append(Reports.filter(deleted=False, store=store,
                                               product=prod)
                                .order_by(Reports.date.desc()).get())
            except Exception as e:
                # print(e)
                pass
    return list_rep


def lastes_upper_of(value):
    return [(rept) for rept in lastes_reports() if rept.remaining < value]


def update_report(report):
    """ Supression  """
    try:
        p = Reports.filter(deleted=False, date__gt=report.date).get()
        p.save()
    except Exception as e:
        print("update_report", e)
        pass

    report.delete_instance()


def multi_store(self):
    return Store.select().count() > 1


def check_befor_update_data(report):
    print("check_befor_update_data")
    from models import Reports
    # list_error = []
    if report.prev_rpt():
        remaining = report.prev_rpt().remaining
    else:
        remaining = 0
    for rpt in report.next_rpts():
        if rpt.type_ == Reports.E:
            remaining += rpt.qty_use
        if rpt.type_ == Reports.S:
            remaining -= rpt.qty_use
        print(remaining)
        if remaining < 0:
            return remaining, False
            break
    return 0, True
