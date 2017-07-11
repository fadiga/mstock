#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (unicode_literals, absolute_import, division,
                        print_function)
import os
# from static import Constants
from Common.cstatic import CConstants

ROOT_DIR = os.path.dirname(os.path.abspath('__file__'))


class Config(CConstants):

    """ docstring for Config
                            """

    def __init__(self):
        CConstants.__init__(self)

    # ------------------------- Organisation --------------------------#

    from Common.models import Organization, Version

    try:
        DB_VERS = Version().get(Version.number == 1)
    except:
        DB_VERS = 1
    try:
        sttg = Organization().get(Organization.id == 1)
        # LOGIN = sttg.login
        NAME_ORGA = sttg.name_orga
        TEL_ORGA = sttg.phone
        ADRESS_ORGA = sttg.adress_org
        BP = sttg.bp
        EMAIL_ORGA = sttg.email_org
        # DEBUG = True
    except Exception as e:
        print(e)
    # DEBUG = True
    # DEBUG = False

    # des_image_record = "static/img_prod"
    ARMOIRE = "img_prod"
    des_image_record = os.path.join(ROOT_DIR, ARMOIRE)
    PEEWEE_V = 224
    credit = 17
    tolerance = 50
    nb_warning = 5
    ORG_LOGO = None

    # -------- Application -----------#

    NAME_MAIN = "main.py"

    pdf_source = "pdf_source.pdf"
    APP_NAME = "M. Stock"

    APP_VERSION = u"1.0"
    APP_DATE = u"03/2017"
    img_media = os.path.join(os.path.join(ROOT_DIR, "static"), "images/")
    APP_LOGO = os.path.join(img_media, "logo.png")
    APP_LOGO_ICO = os.path.join(img_media, "logo.ico")

    # # ------------------------- Organisation --------------------------#

    # NAME_ORGA = u"BOUTIQUE ULTIMO"
    # CONTACT_ORGA = u"Bamako-Rep. du Mali"
    # TEL_ORGA = u"20229770/79429471/76422142"
    # ADRESS_ORGA = u"Bamako bozola"
    # BP = u"B.P:177"
    # EMAIL_ORGA = u"ultimomalidk@yahoo.fr"
