# -*- mode: python ; coding: utf-8 -*-
# file for automatic creation of app with pyinstaller. After app can be packed with InsallForge

added_files = [
         ( 'src/logging.conf', '.' ),
         ( 'src/packages.conf', '.' )
         ]

a = Analysis(
    ['src\\app_main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=['deconvolutor.main', 'extractor.main', 'example_package.main'],
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
    name='app_main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app_main',
)
