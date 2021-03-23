#  -*- coding: utf-8 -*-
#***************************************************************************
#* Copyright (C) 2020 by Andreas Langhoff *
#* <andreas.langhoff@frm2.tum.de> *
#* This program is free software; you can redistribute it and/or modify *
#* it under the terms of the GNU General Public License v3 as published *
#* by the Free Software Foundation; *
# **************************************************************************


from nicos.guisupport.qt import QMenu, pyqtSlot, QAction, QWidget, QDialog, QPushButton
from nicos.guisupport.qt import Qt, QPen, uic, QImage, QTextCharFormat, QPainter, QBrush, QColor
import nicos_mlz.sans1_charming.gui.clients.panels.polygon as polygon
from pathlib import Path
import cv2 as cv
import numpy as np
import json
import copy

win = None

class Window(QWidget):
    def __init__(self, client, ldevname):
        super(Window, self).__init__()
        parent = Path(__file__).resolve().parent
        uipath = parent.joinpath('roieditor.ui')
        uic.loadUi(uipath, self)
        self.client = client
        self.ldevname = ldevname
        params = self.client.getDeviceParams(ldevname)
        self.backgroundimage = params['backgroundimage']

        self.image = None
        self.bZoom.setChecked(True)
        self.filter1.setChecked(True)
        self.zoom = self.bZoom.isChecked()
        self.noredrawblack = False
        self.tf = QTextCharFormat()
        self.polylist = []
        self.polylistindex = len(self.polylist)
        self.RoicomboBox.insertItem(0, "add")
        self.writeWKT.setEnabled(False)
        self.editRoiBtn.setEnabled(False)
        self.addPolygon()
        self.RoicomboBox.currentIndexChanged.connect(self.on_roi_active_changed)
        self.ineditroi = False
        self.editRoiBtn.clicked.connect(self.on_editRoiBtn_clicked)
        self.wktText.textChanged.connect(self.on_wktText_textchanged)
        self.on_readWKT_clicked()

        self.on_pollData()
        #self.resize(rv[0],rv[1])
    def closeEvent(self, event):
        self.deleteLater()
        event.accept()
        global win
        win = None

    def addPolygon(self):
        self.polylist.append(polygon.Polygon())
        index = len(self.polylist)
        self.RoicomboBox.insertItem(index, str(index))
        self.polylistindex = index
        self.RoicomboBox.setCurrentIndex(self.polylistindex)

    def removePolygon(self, index):
        i = 0
        items = len(self.polylist)
        for cur in self.polylist:
            if i == index:
                self.polylist.remove(cur)
                self.RoicomboBox.removeItem(items)
                self.wktText.setPlainText("")
                break
            i = i + 1

    def on_roi_active_changed(self, value):
        if value == 0:   # ='add'
            self.addPolygon()
        self.polylistindex = self.RoicomboBox.currentIndex()
        self.on_readWKT_clicked()
        if self.polylistindex == 1:
            self.writeWKT.setEnabled(False)
            self.editRoiBtn.setEnabled(False)
        else:
            self.writeWKT.setEnabled(True)
            self.editRoiBtn.setEnabled(True)
        self.repaint()

    @pyqtSlot()
    def on_editRoiBtn_clicked(self):
        if self.ineditroi:
            return
        height, width = self.mat.shape[:2]
        if height < 2 or width < 2:
            return
        if self.polylistindex == 1:
            return
        self.ineditroi = True
        self.polylist[self.polylistindex - 1].vertices().clear()

    def on_wktText_textchanged(self):
        if not  self.noredrawblack:
            self.noredrawblack = True
            txt = self.wktText.toPlainText()
            self.wktText.setCurrentCharFormat(self.tf)
            self.wktText.setPlainText(txt)
            self.wktText.update()


    @pyqtSlot()
    def on_updateBG_clicked(self):
        self.on_pollData()

    @pyqtSlot()
    def on_writeWKT_clicked(self):
        wkt = str(self.wktText.toPlainText())
        arg = 'ROI'+str(self.polylistindex - 1)+':'+wkt
        jcurwkt = self.client.eval(self.ldevname+".roi('"+arg+"')")
        if wkt != "":
            self.on_readWKT_clicked()

    @pyqtSlot()
    def on_readWKT_clicked(self):

        self.noredrawblack = True
        self.tf.setForeground(QBrush(Qt.red))
        self.wktText.setCurrentCharFormat(self.tf)
        arg = 'ROI'+str(self.polylistindex - 1)
        jcurwkt = self.client.eval(self.ldevname+".roi('"+arg+"')")
        if not jcurwkt:
            self.wktText.setPlainText('')
        else:
            curwkt = json.loads(jcurwkt)
            self.wktText.setPlainText(curwkt[0])

        self.polylist[self.polylistindex - 1].readWKT(self.wktText.toPlainText())
        self.tf.setForeground(QBrush(Qt.black))
        self.noredrawblack = False
        self.wktText.update()


    def paintEvent(self, event):
        img = self.image
        self.zoom = self.bZoom.isChecked()
        if img.width() > 256:
            self.zoom = False
            self.bZoom.setChecked(False)
        if self.zoom:
            img = self.image.scaledToWidth(self.image.width() * 2)
        painter = QPainter()
        painter.begin(self)

        painter.drawImage(self.image_frame.x(), self.image_frame.y(), img)

        i = 0
        for poly in self.polylist:
            if i + 1 == self.polylistindex:
                pen = QPen(Qt.red, 2)
            else:
                pen = QPen(Qt.black, 2)
            i = i + 1
            painter.setPen(pen)
            lastdp = None
            for qp in poly.vertices():
                qpz = copy.copy(qp)
                if self.zoom:
                    qpz.setX(qpz.x() * 2)
                    qpz.setY(qpz.y() * 2)

                adp = self.image_frame.mapToParent(qpz)
                if not lastdp is None:
                    painter.drawLine(lastdp, adp)
                lastdp = adp
        painter.end()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.ineditroi is True:
                if self.polylistindex > 1:
                     arg = 'ROI'+str(self.polylistindex - 1)+':'
                     jcurwkt = self.client.eval(self.ldevname+".roi('"+arg+"')")
                     self.removePolygon(self.polylistindex - 1)

            #self.wktText.setPlainText("")
            self.ineditroi = False


    def mousePressEvent(self, event):
        if self.ineditroi:
            if event.button() == Qt.LeftButton:
                mpos = self.image_frame.mapFromParent(event.pos())
                zf = 1
                if self.zoom:
                    mpos /= 2
                    zf = 2

                doprint = True
                if not (mpos.x() >= 0 and mpos.x() <= self.image.width() * zf):
                    doprint = False
                if not (mpos.y() >= 0 and mpos.y() <= self.image.size().height() * zf):
                    doprint = False
                if doprint:
                    self.polylist[self.polylistindex - 1].addPoint(mpos)
                    self.update()

            if event.button() == Qt.RightButton:
                self.polylist[self.polylistindex - 1].close()
                self.ineditroi = False
                wkt = self.polylist[self.polylistindex - 1].WKT()
                self.wktText.setPlainText(wkt)
                self.update()

    def on_pollData(self):
        shape = self.client.eval(self.backgroundimage + '.size')
        data = self.client.eval(self.backgroundimage + ".readArray('live')")
        #print(shape)
        self.mat = data.reshape(shape)

        if shape[0] > 1 and shape[1] > 1:
            img = cv.normalize(np.int32(self.mat), None, 0, 255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)
            #cv.normalize need an image with x and y > 1: It gives best normalization also with high counts per pixel
        else:
            img = (self.mat*255 /max(1, np.amax(data))).astype(np.uint8)

        if self.filter1.isChecked():
            #https://docs.opencv.org/3.4/d5/daf/tutorial_py_histogram_equalization.html
            clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl1 = clahe.apply(img)
            img = cl1


        img = cv.applyColorMap(img, cv.COLORMAP_JET)
        self.image = img
        self.image = QImage(self.image.data, self.image.shape[0], self.image.shape[1], QImage.Format_RGB888).rgbSwapped()
        self.image_frame.repaint()

