# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

root = Path.cwd()
client_dist = root / 'client' / 'dist'
profiles_dir = root / 'profiles'

block_cipher = None

a = Analysis(
    ['server/run_server.py'],
    pathex=[str(root / 'server')],
    binaries=[],
    datas=[
        (str(profiles_dir), 'profiles'),
        (str(client_dist), 'client/dist'),
    ],
    hiddenimports=['uvicorn.logging', 'uvicorn.loops', 'uvicorn.protocols.http'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='kitodan-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
