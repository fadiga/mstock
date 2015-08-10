#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fadiga

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

import os
import sys
sys.path.append(os.path.abspath('../'))
import locale
import gettext
import gettext_windows

from PyQt4.QtGui import QApplication, QStyleFactory

from database import setup

from Common.ui.window import FWindow
from Common.cmain import cmain

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
    setup()
    if cmain():
        main()
