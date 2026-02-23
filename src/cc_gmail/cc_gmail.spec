# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# Collect cc_shared module
cc_shared_datas, cc_shared_binaries, cc_shared_hiddenimports = collect_all('cc_shared')

a = Analysis(
    ['src\\cli.py'],
    pathex=['D:/ReposFred/cc_tools/src/cc_shared'],
    binaries=cc_shared_binaries,
    datas=cc_shared_datas,
    hiddenimports=cc_shared_hiddenimports + [
        'cc_shared',
        'cc_shared.config',
        'rich._unicode_data',
        'rich._unicode_data.unicode17-0-0',
        'rich._unicode_data.unicode16-0-0',
        'rich._unicode_data.unicode15-1-0',
        'rich._unicode_data.unicode15-0-0',
        'rich._unicode_data.unicode14-0-0',
        'rich._unicode_data.unicode13-0-0',
        'rich._unicode_data.unicode12-1-0',
        'rich._unicode_data.unicode12-0-0',
        'rich._unicode_data.unicode11-0-0',
        'rich._unicode_data.unicode10-0-0',
        'rich._unicode_data.unicode9-0-0',
        'rich._unicode_data.unicode8-0-0',
        'rich._unicode_data.unicode7-0-0',
        'rich._unicode_data.unicode6-3-0',
        'rich._unicode_data.unicode6-2-0',
        'rich._unicode_data.unicode6-1-0',
        'rich._unicode_data.unicode6-0-0',
        'rich._unicode_data.unicode5-2-0',
        'rich._unicode_data.unicode5-1-0',
        'rich._unicode_data.unicode5-0-0',
        'rich._unicode_data.unicode4-1-0',
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
    a.binaries,
    a.datas,
    [],
    name='cc_gmail',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
