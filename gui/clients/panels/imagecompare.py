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
        uipath = parent.joinpath('imagecompare.ui')
        uic.loadUi(uipath, self)
        self.client = client
        params = self.client.getDeviceParams(ldevname)
        self.ldevname = [ ldevname, params['compare2']]
        self.image = [None, None]
        self.frame = [self.image_frame, self.compare2_frame]
        self.mat = [None, None]

        self.on_pollData()

    def closeEvent(self, event):
        self.deleteLater()
        event.accept()
        global win
        win = None



    @pyqtSlot()
    def on_update_clicked(self):
        self.on_pollData()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        for i in range(2):
            img = self.image[i]
            painter.drawImage(self.frame[i].x(), self.frame[i].y(), img)
        painter.end()

    def on_pollData(self):
        for i in range(2):
            shape = self.client.eval(self.ldevname[i] + '.size')
            data = self.client.eval(self.ldevname[i] + ".readArray('live')")
            #print(shape)
            self.mat[i] = data.reshape(shape)
            if shape[0] > 1 and shape[1] > 1:
                img = cv.normalize(np.int32(self.mat[i]), None, 0, 255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)
                #cv.normalize need an image with x and y > 1: It gives best normalization also with high counts per pixel
            else:
                img = (self.mat[i]*255 /max(1, np.amax(data))).astype(np.uint8)

           # if self.filter1.isChecked():
           #     #https://docs.opencv.org/3.4/d5/daf/tutorial_py_histogram_equalization.html
           #     clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
           #     cl1 = clahe.apply(img)
           #     img = cl1
            img = cv.applyColorMap(img, cv.COLORMAP_JET)
            self.image[i] = img
            self.image[i] = QImage(self.image[i].data, self.image[i].shape[0], self.image[i].shape[1], QImage.Format_RGB888).rgbSwapped()
            self.frame[i].repaint()

