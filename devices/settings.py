#  -*- coding: utf-8 -*-
#***************************************************************************
#* Copyright (C) 2020 by Andreas Langhoff *
#* <andreas.langhoff@frm2.tum.de> *
#* This program is free software; you can redistribute it and/or modify *
#* it under the terms of the GNU General Public License v3 as published *
#* by the Free Software Foundation; *
# **************************************************************************

"""Settings read / write for charm devices"""
import json
from nicos import session
from nicos.core import  Param,  listof, status, Readable, Override
from nicos.devices.tango import StringIO
from nicos.services.daemon.script import RequestError, ScriptRequest
from nicos.core.utils import usermethod
from nicos.core.params import Value
from time import time as currenttime

class Settings(StringIO,Readable):




    def doInit(self, mode):
        pass
    def doShutdown(self):
        pass

    def available(self):
        n_items = self.availablelines
        delays = []
        cmds =[]
        rois = []
        for i in range(n_items):
            delays.append(0)
            cmd = str(i)
            cmds.append(cmd)
        return  self.multiCommunicate((delays,cmds))


    def read(self, maxage=0):

        rois = self.available()
        x = self.status()
        msg = ''
        all = []
        for rd in rois:
            roidata = json.loads(rd)
            all.append(roidata)

        msg = json.dumps(all)
        self._cache.put(self, 'value', msg, currenttime(), self.maxage)
        # not put in the cache by Tango
        return msg

    def doRead(self, maxage=0):
        return self.read(maxage)


    @usermethod
    def setting(self,*argv):
        """ read or write setting,  read: '0' or 'settingname'.
                               write: 'settingname:value' .
        """
        index = -1
        roidata = self.available()
        if not len(argv):
            print('available:')
            for rd in roidata:
                print(rd)
            return ''
        if len(argv):
            tok = argv[0].split(':')
            for  rd in roidata:
                 d = {}
                 d = json.loads(rd)
                 for b in d.items():
                     if b[0] == tok[0]:
                         if len(tok) > 1:
                             #sloppyness json true/false and python True/False
                             if tok[1] == 'true':
                                 tok[1] = 'True'
                             if tok[1] == 'false':
                                 tok[1] = 'False'
                             cmd = tok[0]+":"+tok[1]
                             return self.communicate(cmd)

                     return rd
                     #return b


