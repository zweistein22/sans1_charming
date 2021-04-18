#  -*- coding: utf-8 -*-
#***************************************************************************
#* Copyright (C) 2019-2020 by Andreas Langhoff *
#* <andreas.langhoff@frm2.tum.de> *
#* This program is free software; you can redistribute it and/or modify *
#* it under the terms of the GNU General Public License as published by *
#* the Free Software Foundation; *
# **************************************************************************

from nicos.guisupport.qt import QMenu, pyqtSlot, QAction, QWidget, QDialog, QPushButton
from nicos.guisupport.qt import Qt, QPen, uic, QImage, QTextCharFormat, QPainter, QBrush, QColor
from pathlib import Path
import json
import copy

win = None



class Window(QWidget):
    def __init__(self, client, ldevname):
        super(Window, self).__init__()
        parent = Path(__file__).resolve().parent
        uipath = parent.joinpath('playlisteditor.ui')
        uic.loadUi(uipath, self)
        self.client = client
        self.ldevname = ldevname
        params = self.client.getDeviceParams(ldevname)
        self.playlist.clicked.connect(self.playlist_clicked)
        self.pbutton_remove.clicked.connect(self.remove_clicked)
        self.pbutton_add.clicked.connect(self.add_clicked)
        self.pbutton_add_directory.clicked.connect(self.add_directory_clicked)
        self.lineEdit.clear()
        self.add_clicked()
        #self.resize(rv[0],rv[1])

    def closeEvent(self, event):
        self.deleteLater()
        event.accept()
        global win
        win = None

    def addlist(self, li):
        if li is not None:
            for i in li:
                self.playlist.clear()
                li2 = self.client.eval(self.ldevname+".addfile('"+i+"')")
                pyli2 = eval(li2)
                self.playlist.addItems(pyli2)


    def playlist_clicked(self):
        item = self.playlist.currentItem()
        self.lineEdit.setText(str(item.text()))

    def remove_clicked(self):
        file = self.lineEdit.text()
        li = self.client.eval(self.ldevname+".removefile('"+file+"')")
        pyli = eval(li)
        self.playlist.clear()
        self.playlist.addItems(pyli)

    def add_clicked(self):
        file = self.lineEdit.text()
        li = self.client.eval(self.ldevname+".addfile('"+file+"')")
        pyli = eval(li)
        self.playlist.clear()
        self.playlist.addItems(pyli)

    def add_directory_clicked(self):
        #print("add_directory_clicked")
        directory = self.lineEdit_directory.text()
        li = self.client.eval(self.ldevname+".files('"+directory+"')")
        pyli = eval(li)
        self.addlist(pyli)


