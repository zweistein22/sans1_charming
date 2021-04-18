import nicos_mlz.sans1_charming.nicospath as nicospath

description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'Sans1',
    experiment = 'Exp',
    datasinks = ['filesink', 'conssink', 'dmnsink', 'livesink','rawsink'],
    notifiers = [],
)


modules = ['nicos.commands.standard']


devices = dict(
    Sans1 = device('nicos.devices.instrument.Instrument',
        description = 'Sans1-charming',
        instrument = 'SANS1',
        responsible = 'andreas langhoff <andreas.langhoff@frm2.tum.de>',
        website = 'http://www.nicos-controls.org',
        operators = ['NICOS developer team'],
        facility = 'NICOS instruments',
    ),
     Sample = device('nicos.devices.sample.Sample',
        description =  'The currently used sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = nicospath.NicosPath.data_dir(),
        sendmail = False,
        serviceexp = 'servicesans1',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        warnlimits = (5., None),
        path = None,
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = '/',
        warnlimits = (.5, None),
        minfree = 0.5,
        lowlevel = False,
    ),


   livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = 'Sends image data to LiveViewWidget',
    ),
    rawsink = device('nicos.devices.datasinks.RawImageSink',
        description = 'Saves image data in RAW format',
        filenametemplate = [
            '%(proposal)s_%(pointcounter)s.raw',
            '%(proposal)s_%(scancounter)s_%(pointcounter)s_%(pointnumber)s.raw'
        ],
    ),

)

