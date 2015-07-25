#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (unicode_literals, absolute_import, division,
                        print_function)

from static import Constants
from Common import peewee


class Config(Constants):
    """ docstring for Config
                            """
    def __init__(self):
        Constants.__init__(self)

    # ------------------------- Organisation --------------------------#

    from Common.models import Organization, Version

    try:
        DB_VERS = Version().get(Version.number == 1)
    except:
        DB_VERS = 1
    try:
        sttg = Organization().get(Organization.id == 1)
        LOGIN = sttg.login
        NAME_ORGA = sttg.name_orga
        TEL_ORGA = sttg.phone
        ADRESS_ORGA = sttg.adress_org
        BP = sttg.bp
        EMAIL_ORGA = sttg.email_org
        DEBUG = True
    except peewee.OperationalError:
        pass

    # DEBUG = True
    DEBUG = False

    # # ------------------------- Organisation --------------------------#
    # NAME_MAIN = "mmain.py"
    # APP_NAME = u"G.mag"
    # APP_DATE = u"12/2012"

    # NAME_ORGA = u"BOUTIQUE ULTIMO"
    # CONTACT_ORGA = u"Bamako-Rep. du Mali"
    # TEL_ORGA = u"20229770/79429471/76422142"
    # ADRESS_ORGA = u"Bamako bozola"
    # BP = u"B.P:177"
    # EMAIL_ORGA = u"ultimomalidk@yahoo.fr"
