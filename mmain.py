#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fadiga

from __future__ import (unicode_literals, absolute_import, division, print_function)

import os, sys; sys.path.append(os.path.abspath('../'))
import locale
import gettext, gettext_windows

from PyQt4.QtGui import QApplication, QDialog, QStyleFactory

from database import setup
from configuration import Config
from Common.models import SettingsAdmin

from Common.ui.window import FWindow
from Common.ui.login import LoginWidget, john_doe
from Common.ui.license_view import LicenseViewWidget

from ui.mainwindow import MainWindow

app = QApplication(sys.argv)
# app.setStyle(QStyleFactory.create("cleanlooks"))

def main():
    """  """
    gettext_windows.setup_env()
    locale.setlocale(locale.LC_ALL, '')
    # gettext.install('mmain', localedir='locale', unicode=True)
    gettext.install('mmain', localedir='locale')
    window = MainWindow()
    setattr(FWindow, 'window', window)
    window.show()
    # window.showMaximized()
    sys.exit(app.exec_())

if __name__ == '__main__':
    if Config.DEBUG:
        print("DEBUG")
        john_doe()
        main()
    elif not SettingsAdmin().get(SettingsAdmin.id == 1).can_use:
        if LicenseViewWidget(parent=None).exec_() == QDialog.Accepted:
            main()
    elif LoginWidget().exec_() == QDialog.Accepted:
        main()
