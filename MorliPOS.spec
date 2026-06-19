# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['index.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('database.db', '.'),
        ('clientes.db', '.'),
        ('codigos.db', '.'),
        ('icono.ico', '.'),
        ('codigos', 'codigos'),
        ('corte_z', 'corte_z'),
        ('facturas', 'facturas'),
        ('imagenes', 'imagenes'),
        ('ui', 'ui'),
        ('logica', 'logica'),
        ('utils', 'utils'),
    ],
    hiddenimports=[
       'reportlab.graphics.barcode.code128',
    'reportlab.graphics.barcode.code39',
    'reportlab.graphics.barcode.code93',
    'reportlab.graphics.barcode.eanbc',
    'reportlab.graphics.barcode.fourstate',
    'reportlab.graphics.barcode.qr',
    'reportlab.graphics.barcode.usps',
    'reportlab.graphics.barcode.usps4s',
    'reportlab.graphics.barcode.common',
    'reportlab.graphics.barcode.ecc200datamatrix',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MorliPOS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icono.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MorliPOS',
)