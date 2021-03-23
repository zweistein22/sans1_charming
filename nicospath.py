import nicos
import os

class NicosPath:

 @staticmethod
 def root():

     nicos_root = os.path.normpath(os.path.dirname(os.path.dirname(os.path.abspath(nicos.__file__))))
     newPath = nicos_root.replace(os.sep, '/')
     print('nicos_root=' + newPath)
     return newPath

 @staticmethod
 def live_png():
     lvg = os.path.join(NicosPath.root(),'bin/data/live_lin.png')
     lvg_1 = lvg.replace(os.sep,'/')
     print('live_png() = ' + lvg_1)
     return lvg_1

 @staticmethod
 def live2_png():
     lvg = os.path.join(NicosPath.root(),'bin/data/live2_lin.png')
     lvg_1 = lvg.replace(os.sep,'/')
     print('live2_png() = ' + lvg_1)
     return lvg_1

 @staticmethod
 def data_dir():
     lvg = os.path.join(NicosPath.root(),'bin/data')
     lvg_1 = lvg.replace(os.sep,'/')
     return lvg_1

