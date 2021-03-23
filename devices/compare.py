#  -*- coding: utf-8 -*-
#***************************************************************************
#* Copyright (C) 2020 by Andreas Langhoff *
#* <andreas.langhoff@frm2.tum.de> *
#* This program is free software; you can redistribute it and/or modify *
#* it under the terms of the GNU General Public License v3 as published *
#* by the Free Software Foundation; *
# **************************************************************************

"""Compare 2 Images ... and in the future add comparison algoritm result."""
import json
from nicos import session
from nicos.core import  Param,  listof, status, Readable, Override
from nicos.services.daemon.script import RequestError, ScriptRequest
from nicos.core.utils import usermethod
from nicos.core.params import Value
from nicos.devices.tango import ImageChannel
from nicos.core.status import BUSY, OK
from time import time as currenttime
from nicos_mlz.sans1_charming.devices.detector import CharmImageChannel


class Image(CharmImageChannel):

    parameters = {
         'compare2': Param('compare2',type=str),
    }


    def doInit(self, mode):
        pass
    def doShutdown(self):
        pass

