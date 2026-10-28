# -*- mode: python ; coding: utf-8 -*-
import os
import sys

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# collect_submodules importa los paquetes: Hotel/ debe estar en sys.path ANTES de llamarlo,
# si no, las apps de Django (users, hotel, caja...) no quedan dentro del .exe.
HOTEL_DIR = os.path.join(SPECPATH, 'Hotel')
sys.path.insert(0, HOTEL_DIR)

hiddenimports = ['config', 'config.settings', 'config.wsgi']
hiddenimports += collect_submodules('config')
hiddenimports += collect_submodules('users')
hiddenimports += collect_submodules('hotel')
hiddenimports += collect_submodules('market')
hiddenimports += collect_submodules('caja')
hiddenimports += collect_submodules('cochera')
hiddenimports += collect_submodules('recados')
hiddenimports += collect_submodules('core')
hiddenimports += collect_submodules('django')
hiddenimports += collect_submodules('rest_framework')
hiddenimports += collect_submodules('rest_framework_simplejwt')
hiddenimports += collect_submodules('corsheaders')
hiddenimports += collect_submodules('django_filters')

# Traducciones y plantillas de las librerías (mensajes de error en español, etc.).
extra_datas = []
for package in ('django', 'rest_framework', 'rest_framework_simplejwt', 'django_filters', 'corsheaders'):
    extra_datas += collect_data_files(package)

a = Analysis(
    ['main.py'],
    pathex=[HOTEL_DIR],
    binaries=[],
    datas=[(os.path.join(SPECPATH, 'frontend_build'), 'frontend_build')] + extra_datas,
    hiddenimports=hiddenimports,
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
    a.binaries,
    a.datas,
    [],
    name='Hotel Venecia',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
