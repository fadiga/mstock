#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fadiga

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

import os
import sys

from PyQt4.QtGui import QApplication


sys.path.append(os.path.abspath('../'))

from ui.mainwindow import MainWindow
from Common.ui.window import FWindow
from Common.ui.qss import theme
from Common.cmain import cmain


app = QApplication(sys.argv)


def main():
    """  """
    window = MainWindow()
    window.setStyleSheet(theme)
    setattr(FWindow, 'window', window)
    # window.show()
    window.showMaximized()
    sys.exit(app.exec_())

if __name__ == '__main__':
    if cmain():
        main()
