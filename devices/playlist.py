#  -*- coding: utf-8 -*-
#***************************************************************************
#* Copyright (C) 2020 by Andreas Langhoff *
#* <andreas.langhoff@frm2.tum.de> *
#* This program is free software; you can redistribute it and/or modify *
#* it under the terms of the GNU General Public License v3 as published *
#* by the Free Software Foundation; *
# **************************************************************************

"""Playlist Manager"""
import json
from nicos import session
from nicos.core import  Param,  listof, status, Readable, Override
from nicos.devices.tango import StringIO
from nicos.services.daemon.script import RequestError, ScriptRequest
from nicos.core.utils import usermethod
from nicos.core.params import Value
from nicos.core.status import WARN
from time import time as currenttime

class Manager(StringIO,Readable):


    parameter_overrides = {
        'pollinterval': Override(default=15),  # every 5 seconds
    }

    def doInit(self, mode):
        pass
    def doShutdown(self):
        pass

    def read(self, maxage=0):

        rois = self.addfile("")
        msg = json.loads(rois)
        self._cache.put(self, 'value', msg, currenttime(), self.maxage)
        # not put in the cache by Tango
        return msg

    def doRead(self, maxage=0):
        return self.read(maxage)

    def doStatus(self, maxage=0):
        state = super().doStatus(maxage)
        if not len(state[1]):
             return (WARN, state[1])
        return state




    def internCommunicate(self, name, arg):
        stringio = name+':'+'["'+arg+'"]'
        rv = self.communicate(stringio)
        return rv

    @usermethod
    def files(self,*argv):
        """ shows available listmode files (.mdat) in a directory on the remote server.
              files("~")  returns available files in the home directory
        """
        if not len(argv):
             print("argument missing:")
             print("specify directory to search.")
             print("no action taken.")
             return []
        if len(argv) > 1:
             print("too many arguments:")
             print("no action taken.")
             return []
        return self.internCommunicate("FilesInDirectory",argv[0])


    @usermethod
    def removefile(self,*argv):
        """ remove  file to playlist.
             returns current playlist.
        """
        toremove = ''
        if not len(argv):
             print("argument missing:")
             print("specify file to remove from playlist.")
        if len(argv) > 1:
             print("too many arguments:")
             print("no action taken.")
             return []
        if len(argv) == 1:
             toremove = argv[0]
        return self.internCommunicate("RemoveFile",toremove)

    @usermethod
    def addfile(self,*argv):
        """ add file to playlist.
            returns current playlist.
        """
        toadd = ''
        if len(argv) > 1:
             print("too many arguments:")
             print("no action taken.")
             return []
        if len(argv) == 1:
             toadd = argv[0]
        return self.internCommunicate("AddFile",toadd)


    @usermethod
    def setting(self,*argv):
        """ read or write setting,  read: '0' or 'settingname'.
                               write: 'settingname:value' .
        """
        index = -1
        __ALL_ATTRIBUTES__ = ['speedmultiplier']

        if not len(argv):
            print('available:')
            for rd in __ALL_ATTRIBUTES__:
                print(rd)
            return ''
        if len(argv):
            tok = argv[0].split(':')
            for  rd in __ALL_ATTRIBUTES__:
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

