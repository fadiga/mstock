#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fadiga

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

import os
import sys
# import locale
# import gettext
import gettext_windows

from PyQt4.QtGui import QApplication


sys.path.append(os.path.abspath('../'))

from database import setup
from ui.mainwindow import MainWindow
from Common.ui.window import FWindow
from Common.ui.qss import appStyle
from Common.cmain import cmain


app = QApplication(sys.argv)


def main():
    """  """
    gettext_windows.setup_env()
    # locale.setlocale(locale.LC_ALL, '')
    # gettext.install('mmain', localedir='locale', unicode=True)
    # gettext.install('main.py', localedir='locale')
    window = MainWindow()
    window.setStyleSheet(appStyle)
    setattr(FWindow, 'window', window)
    window.show()
    # window.showMaximized()
    sys.exit(app.exec_())

if __name__ == '__main__':
    setup()
    if cmain():
        main()
