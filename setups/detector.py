description = 'SANS1 detector'

group = 'basic'

includes = ['sans1']

excludes = []

devices = dict(sans1 = device('nicos.devices.generic.detector.Detector',
        description = 'Charm or Mesytec 2D Neutron detector',
        timers = ['timer'],
        counters = ['counter'],
        monitors =['monitor0','monitor1','monitor2','monitor3'],
        images = ['histogram','histogramraw'],
        liveinterval = 1.0,
        pollinterval = 1,
        maxage = 1,),)

