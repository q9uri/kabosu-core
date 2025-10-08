# -*- mode: python ; coding: utf-8 -*-
# このファイルは元々 PyInstaller によって自動生成されたもので、それをカスタマイズして使用しています。
import sys; sys.setrecursionlimit(sys.getrecursionlimit() * 10)

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules
from pathlib import Path
import re
import sys

datas = []
datas += collect_data_files('e2k')
datas += collect_data_files('unidic_lite')
datas += collect_data_files('yomikata')
datas += collect_data_files('kabosu_core')
datas += collect_data_files('kabosu_plus')
datas += collect_data_files('g2p_en')

# functorch のバイナリを収集
# ONNX に移行したため不要なはずだが、念のため
binaries = collect_dynamic_libs('functorch')

# Windows: Intel MKL 関連の DLL を収集
# これをやらないと PyTorch が CPU 版か CUDA 版かに関わらずクラッシュする…
# ONNX に移行したため不要なはずだが、念のため
if sys.platform == 'win32':
    lib_dir_path = Path(sys.prefix) / 'Library' / 'bin'
    if lib_dir_path.exists():
        mkl_dlls = list(lib_dir_path.glob('*.dll'))
        for dll in mkl_dlls:
            binaries.append((str(dll), '.'))

block_cipher = None

# ライブラリの噛み合わせが悪いのか、なぜか標準ライブラリの dataclasses に
# __version__ 変数が存在しないと PyInstaller ビルドに失敗する
# 大昔 dataclasses が標準ライブラリで存在しなかった頃の名残なのか…？
# これをどうにか回避するため、苦肉の策ではあるがビルド時だけ dataclasses.py の場所を探して追記する
base_prefix = getattr(sys, 'base_prefix', sys.prefix)
if sys.platform == 'win32':
    dataclasses_path = Path(base_prefix) / 'Lib' / 'dataclasses.py'
else:
    dataclasses_path = Path(base_prefix) / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'dataclasses.py'
try:
    with dataclasses_path.open(mode='a', encoding='utf-8') as file:
        file.write('\n__version__ = "1.0"')
    print(f'Added __version__ to {dataclasses_path}')
except Exception as e:
    print(f'Error while writing to dataclasses.py: {e}')

hiddenimports=[
    # ref: https://github.com/pypa/setuptools/issues/4374
    'pkg_resources.extern',
    # NumPy 2.x で生成した Pickle を含む .npy/.npz ファイルを NumPy 1.x で読み込むために必要
    # numpy._core 以下のダミーモジュールを明示的に hiddenimports に追加しないと ModuleNotFoundError が発生する
    # ref: https://github.com/numpy/numpy/issues/24844
    'numpy._core',
    'numpy._core._dtype_ctypes',
    'numpy._core._dtype',
    'numpy._core._internal',
    'numpy._core._multiarray_umath',
    'numpy._core.multiarray',
    'numpy._core.umath',
]
#強制的にtransformersをすべて含める
hiddenimports += collect_submodules("transformers")

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    module_collection_mode={
        # Style-Bert-VITS2 内部で使われている TorchScript (@torch.jit) による問題を回避するために必要
        'style_bert_vits2': 'pyz+py',
        'inflect': 'pyz+py',
    },
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='run',
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='run',
)

# ビルド時だけ追記した __version__ を削除
try:
    with dataclasses_path.open(mode='r+', encoding='utf-8') as file:
        content = file.read()
        content = re.sub(r'\n__version__ = "1\.0"', '', content)
        file.seek(0)
        file.write(content)
        file.truncate()
    print(f'Removed __version__ from {dataclasses_path}')
except Exception as e:
    print(f'Error while writing to dataclasses.py: {e}')
