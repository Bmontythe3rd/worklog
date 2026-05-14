# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

try:
    import customtkinter
    ctk_datas = [(str(Path(customtkinter.__file__).parent), 'customtkinter')]
except ImportError:
    ctk_datas = []

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=ctk_datas,
    hiddenimports=[
        'customtkinter',
        'darkdetect',
        'packaging',
        'packaging.version',
        'packaging.specifiers',
        'packaging.requirements',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Worklog',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    argv_emulation=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='Worklog',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='Worklog.app',
        icon=None,
        bundle_identifier='tech.montymail.worklog',
        info_plist={
            'CFBundleName': 'Worklog',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        },
    )
