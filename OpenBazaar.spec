# -*- mode: python -*-
a = Analysis(['node/tornadoloop.py'],
             pathex=['/Users/brianhoffman/Projects/OB/OpenBazaar'],
             hiddenimports=['zmq.backend.select','zmq.core.pysocket','zmq.utils.strtypes', 'zmq.utils.jsonapi'],
             hookspath='../hooks',
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='OpenBazaar',
          debug=False,
          strip=None,
          upx=True,
          console=True )
