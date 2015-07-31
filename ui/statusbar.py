#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: fadiga

from PyQt4 import QtGui

from models import Owner
from configuration import Config


CONTACTS =  u"<b>Tel:</b> (223)76 43 38 90\n" + \
            u"<b>E-mail:</b> ibfadiga@gmail.com "
AUTOR = u" Ibrahima Fadiga "
PROFFECTION = u" développeur "

class GStatusBar(QtGui.QStatusBar):

    def __init__(self, parent):

        QtGui.QStatusBar.__init__(self, parent)

        self.showMessage(u"""Bienvenue! dans {nameApp} un outil rapide et facile à utiliser qui vous permet de faire le suivi de stock""".format(nameApp=Config.APP_NAME),
                         14000)

        self.setWindowOpacity(1.78)
        self.startTimer(10000)

    def timerEvent(self, event):
        try:
            user = Owner.get(islog=True)
            self.showMessage(u"%s %s est connecté."
                             % (user.group, user.username), 2000)
        except:
            self.showMessage(u"Vos identifiants", 3000)

