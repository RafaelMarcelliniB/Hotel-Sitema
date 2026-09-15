 # -*- mode: python ; coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.abspath('Hotel'))

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = [
    'config', 'config.settings', 'config.wsgi',
    'users', 'users.admin', 'users.apps', 'users.models', 'users.repositories',
    'users.serializers', 'users.services', 'users.tests', 'users.urls', 'users.views',
]
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


a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('Hotel')],
    binaries=[],
    datas=[
        ('frontend_build', 'frontend_build'),
        ('Hotel/users', 'Hotel/users'),
    ],
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
