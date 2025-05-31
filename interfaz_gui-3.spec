# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['interfaz_gui-3.py'],
    pathex=[],
    binaries=[],
    datas=[('base_datos', 'base_datos'), ('fotos_registro', 'fotos_registro'), ('y_true.csv', '.'), ('haarcascade_frontalface_default.xml', '.')],
    hiddenimports=[],
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
    name='interfaz_gui-3',
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
    icon=['asistencia.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='interfaz_gui-3',
)
