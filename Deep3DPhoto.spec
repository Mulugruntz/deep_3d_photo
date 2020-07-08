# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from pathlib import Path
import vispy.scene
import vispy.io
import vispy.visuals
import vispy.glsl
import moviepy
import scipy.special.cython_special

data_files = [
    (os.path.dirname(vispy.glsl.__file__), os.path.join("vispy", "glsl")),
    (os.path.dirname(vispy.scene.__file__), os.path.join("vispy", "scene")),
    (os.path.join(os.path.dirname(vispy.io.__file__), "_data"), os.path.join("vispy", "io", "_data")),
    (os.path.dirname(vispy.visuals.__file__), os.path.join("vispy", "visuals")),
]

hidden_imports = [
    "vispy.ext._bundled.six",
    "vispy.app.backends._wx",
    "pkg_resources.py2_warn",
    "moviepy.audio.fx",
]


def get_size(tree: Tree) -> int:
    fullsize = 0
    l = []
    for resfilename, fullfilename, typecode in tree:
        size = Path(fullfilename).lstat().st_size
        fullsize += size
        l.append((size, fullfilename))
    return fullsize, l


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"


a = Analysis(['main.py'],
             pathex=['src', '3d-photo-inpainting', '/Users/sgiffard/PycharmProjects/deep_3d_photo/Deep3DPhotoApp'],
             binaries=[],
             datas=data_files,
             hiddenimports=hidden_imports,
             hookspath=[],
             runtime_hooks=[],
             excludes=['enchant', 'twisted', '_tkinter', 'Tkinter'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += Tree(os.path.dirname(moviepy.__file__), prefix='moviepy')
a.datas += Tree(os.path.dirname(scipy.special.cython_special.__file__), prefix='scipy.special.cython_special')

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Deep3DPhoto',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )

files = Tree('/Users/sgiffard/PycharmProjects/deep_3d_photo/',
             excludes=[
                 'Deep3DPhotoApp', 'depth', 'mesh', 'models', '.git',
                 'checkpoints', 'image', '*.mp4', '*.pth', '*.pt', '*ply'
             ]
         )
fullsize, sizedtree = get_size(files)
print('\n'.join(f"{sizeof_fmt(item[0]):<10} => {item[1]}" for item in sorted(sizedtree, reverse=True)))
print(f'Full size: {sizeof_fmt(fullsize)} for {len(sizedtree)} files!')

coll = COLLECT(exe, files,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Deep3DPhoto')
app = BUNDLE(coll,
             name='Deep3DPhoto.app',
             icon=None,
             bundle_identifier=None)
