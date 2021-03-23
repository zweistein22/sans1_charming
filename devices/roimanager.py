#  -*- coding: utf-8 -*-
#***************************************************************************
#* Copyright (C) 2020 by Andreas Langhoff *
#* <andreas.langhoff@frm2.tum.de> *
#* This program is free software; you can redistribute it and/or modify *
#* it under the terms of the GNU General Public License v3 as published *
#* by the Free Software Foundation; *
# **************************************************************************

"""Intelligent RoiManager using polygons.(extendible to outer ring / inner ring polygons)"""
import json
from nicos import session
from nicos.core import  Param,  listof, status, Readable, Override
from nicos.devices.tango import StringIO
from nicos.services.daemon.script import RequestError, ScriptRequest
from nicos.core.utils import usermethod
from nicos.core.params import Value
from time import time as currenttime

class RoiManager(StringIO,Readable):

    parameters = {
        'backgroundimage': Param('backgroundimage',type=str),
    }

    parameter_overrides = {
        'pollinterval': Override(default=5),  # every 5 seconds
    }

    def doInit(self, mode):
        pass
    def doShutdown(self):
        pass

    def roidata(self):
        n_items = self.availablelines
        delays = []
        cmds =[]
        rois = []
        for i in range(n_items):
            delays.append(0)
            cmd = "ROI" + str(i)
            cmds.append(cmd)
        return  self.multiCommunicate((delays,cmds))


    def read(self, maxage=0):

        rois = self.roidata()
        x = self.status()
        msg = '['
        i = 0
        for rd in rois:
            if i > 0:
                msg += ', '
            roidata = json.loads(rd)
            msg += str(roidata[1])
            i = i+1
        msg += ']' + ' energy unit cts'
        self._cache.put(self, 'value', msg, currenttime(), self.maxage)
        # not put in the cache by Tango
        return msg

    def doRead(self, maxage=0):
        return self.read(maxage)


    @usermethod
    def roi(self,*argv):
        """ read or write roi,  read: 'ROI0' .
                               write: 'ROI0:POLYGON((0 0, 0 128, 100 128, 100 0, 0 0))' .
        """
        index = -1
        roidata = self.roidata()
        if not len(argv):
            print('available:')
            for rd in roidata:
                print(rd)
            return ''
        if len(argv):
            tok = argv[0].split(':')
            if tok[0].startswith('ROI'):
                istr = tok[0][3:].strip()
                index = int(istr)
            maxindex = len(roidata)
            if len(tok) >= 2:
                maxindex = maxindex+1

            if index >= maxindex or index < 0:

                  print('index out of range. No action taken.')
                  print('available:')
                  for rd in roidata:
                      print(rd)
                  return ''

            if len(tok) < 2:

                return roidata[index]

            else:
                rv = self.communicate(argv[0])
                return rv

