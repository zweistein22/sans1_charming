#  -*- coding: utf-8 -*-
#***************************************************************************
#* Copyright (C) 2020 by Andreas Langhoff *
#* <andreas.langhoff@frm2.tum.de> *
#* This program is free software; you can redistribute it and/or modify *
#* it under the terms of the GNU General Public License v3 as published *
#* by the Free Software Foundation; *
# **************************************************************************


from nicos.clients.gui.panels.devices import DevicesPanel, DEVICE_TYPE
from nicos.guisupport.qt import QMenu,  pyqtSlot, QAction, QWidget, QDialog, QPushButton, uic, QImage, QTextCharFormat, QPainter
from functools import partial

import nicos_mlz.sans1_charming.gui.clients.panels.roieditor as roieditor
import nicos_mlz.sans1_charming.gui.clients.panels.imagecompare as imagecompare
import nicos_mlz.sans1_charming.gui.clients.panels.playlisteditor as playlisteditor

charmpowersupply  = 'nicos_mlz.erwin_charming.devices.charm_HV.CharmPowerSupply' #c p s
roimanager = 'nicos_mlz.sans1_charming.devices.roimanager.RoiManager'
compareimage = 'nicos_mlz.sans1_charming.devices.compare.Image'
playlistmanager = 'nicos_mlz.sans1_charming.devices.playlist.Manager'

class DevicesPanel1(DevicesPanel):

    def on_tree_customContextMenuRequested(self, point):

        item = self.tree.itemAt(point)
        if item is None:
            return
        if item.type() == DEVICE_TYPE:
            self._menu_dev = item.text(0)
            ldevname = self._menu_dev.lower()
            if charmpowersupply in self._devinfo[ldevname].classes:
                 params = self.client.getDeviceParams(ldevname)
                 self.cpsmenu = QMenu()
                 self.cps_actions = []
                 i = 0
                 for menuItem in params['transitions']:
                     self.cps_actions.append(QAction(menuItem))
                     self.cpsmenu.addAction(self.cps_actions[i])
                     self.cps_actions[i].triggered.connect(partial(self.on_actionApply_triggered,i))
                     i = i + 1
                 self.cpsmenu.addSeparator()
                 self.cpsmenu.addAction(self.actionMove)
                 self.cpsmenu.addAction(self.actionReset)
                 self.cpsmenu.addSeparator()
                 if self.mainwindow.history_wintype is not None:
                     self.cpsmenu.addAction(self.actionPlotHistory)
                 self.cpsmenu.addSeparator()
                 self.cpsmenu.addAction(self.actionShutDown)
                 self.cpsmenu.addAction(self.actionHelp)
                 self.cpsmenu.popup(self.tree.viewport().mapToGlobal(point))
                 return

            if roimanager in self._devinfo[ldevname].classes:
                params = self.client.getDeviceParams(ldevname)
                self.cpsmenu = QMenu()
                self.cps_actions = []
                self.cps_actions.append(QAction('Edit...'))
                self.cpsmenu.addAction(self.cps_actions[0])
                self.cps_actions[0].triggered.connect(partial(self.on_roimanagerEdit,ldevname))
                self.cpsmenu.addSeparator()
                self.cpsmenu.addAction(self.actionMove)
                self.cpsmenu.addAction(self.actionReset)
                self.cpsmenu.addSeparator()
                if self.mainwindow.history_wintype is not None:
                    self.cpsmenu.addAction(self.actionPlotHistory)
                self.cpsmenu.addSeparator()
                self.cpsmenu.addAction(self.actionShutDown)
                self.cpsmenu.addAction(self.actionHelp)
                self.cpsmenu.popup(self.tree.viewport().mapToGlobal(point))
                return

            if compareimage in self._devinfo[ldevname].classes:
                params = self.client.getDeviceParams(ldevname)
                self.cpsmenu = QMenu()
                self.cps_actions = []
                self.cps_actions.append(QAction('Show &Compare...'))
                self.cpsmenu.addAction(self.cps_actions[0])
                self.cps_actions[0].triggered.connect(partial(self.on_images_compare,ldevname))
                self.cpsmenu.addSeparator()
                self.cpsmenu.addAction(self.actionMove)
                self.cpsmenu.addAction(self.actionReset)
                self.cpsmenu.addSeparator()
                if self.mainwindow.history_wintype is not None:
                    self.cpsmenu.addAction(self.actionPlotHistory)
                self.cpsmenu.addSeparator()
                self.cpsmenu.addAction(self.actionShutDown)
                self.cpsmenu.addAction(self.actionHelp)
                self.cpsmenu.popup(self.tree.viewport().mapToGlobal(point))
                return

            if playlistmanager in self._devinfo[ldevname].classes:
                params = self.client.getDeviceParams(ldevname)
                self.cpsmenu = QMenu()
                self.cps_actions = []
                self.cps_actions.append(QAction('Edit...'))
                self.cpsmenu.addAction(self.cps_actions[0])
                self.cps_actions[0].triggered.connect(partial(self.on_playlist_edit,ldevname))
                self.cpsmenu.addSeparator()
                self.cpsmenu.addAction(self.actionMove)
                self.cpsmenu.addAction(self.actionReset)
                self.cpsmenu.addSeparator()
                if self.mainwindow.history_wintype is not None:
                    self.cpsmenu.addAction(self.actionPlotHistory)
                self.cpsmenu.addSeparator()
                self.cpsmenu.addAction(self.actionShutDown)
                self.cpsmenu.addAction(self.actionHelp)
                self.cpsmenu.popup(self.tree.viewport().mapToGlobal(point))
                return

        return super().on_tree_customContextMenuRequested( point)

    @pyqtSlot()
    def on_playlist_edit(self,ldevname):
        if not playlisteditor.win:
            playlisteditor.win = playlisteditor.Window(self.client, ldevname)
            playlisteditor.win.show()


    @pyqtSlot()
    def on_images_compare(self,ldevname):
        if not imagecompare.win:
            imagecompare.win = imagecompare.Window(self.client, ldevname)
            imagecompare.win.show()


    @pyqtSlot()
    def on_roimanagerEdit(self,ldevname):
        if not roieditor.win:
            roieditor.win = roieditor.Window(self.client,ldevname)
            roieditor.win.show()


    @pyqtSlot()
    def on_actionApply_triggered(self,index):
        if self._menu_dev:
            self.client.eval(self._menu_dev+'.apply('+str(index)+')')

    def on_client_cache(self, data):
        rv = super().on_client_cache(data)

        # here we truncate the long status message for charmpowersupply devices
        (time, key, op, value) = data
        if '/' not in key:
            return
        ldevname, subkey = key.rsplit('/', 1)
        if ldevname not in self._devinfo:
            return

        devitem = self._devitems[ldevname]
        devinfo = self._devinfo[ldevname]

        if charmpowersupply in self._devinfo[ldevname].classes:
            if subkey == 'status':
                 t = devitem.text(2)
                 i = t.rfind('[')
                 if i >=0:
                     t = t[:i-1]
                 devitem.setText(2,str(t))
            if ldevname in self._control_dialogs:
                    dlg = self._control_dialogs[ldevname]
                    ct = dlg.statuslabel.text()
                    i = ct.rfind('[')
                    if i >=0:
                        ct = ct[:i-1]
                    dlg.statuslabel.setText(ct)

        return rv



