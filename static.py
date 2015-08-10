#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# Maintainer: Fad

import os

from Common.cstatic import CConstants

ROOT_DIR = os.path.dirname(os.path.abspath('__file__'))


class Constants(CConstants):

    def __init__(self):
        CConstants.__init__(self)

    # des_image_record = "static/img_prod"
    # ARMOIRE = "img_prod"
    # des_image_record = os.path.join(ROOT_DIR, ARMOIRE)

    PEEWEE_V = 224
    credit = 17
    tolerance = 50
    nb_warning = 5
    # type_period = W
    # type_period = M
    # DEBUG = False
    DOC_SUPPORT = "*.gif *.png *.jpg *.doc *.docx *.pdf *.jpeg"
    # -------- Application -----------#

    NAME_MAIN = "mmain.py"
    APP_NAME = u"Gestion de Stock"
    pdFsource = "pdFsource.pdf"

    APP_VERSION = u"3.0.0"
    APP_DATE = u"02/2015"
    img_media = os.path.join(os.path.join(ROOT_DIR, "static"), "images/")
    APP_LOGO = os.path.join(img_media, "logo.png")
    APP_LOGO_ICO = os.path.join(img_media, "logo.ico")