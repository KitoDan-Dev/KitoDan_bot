# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

root = Path.cwd()

block_cipher = None

a = Analysis(
    ['server/tray_app.py'],
    pathex=[str(root / 'server')],
    binaries=[],
    datas=[],
    hiddenimports=['pystray._win32', 'PIL.Image', 'PIL.ImageDraw'],
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
    name='kitodan-tray',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
