SET build_tools=%~dp0
SET build_tools=%build_tools:~0,-1%
SET winbuild=%build_tools%\..\winbuild

if exist "%winbuild%" rmdir /s /q "%winbuild%"
mkdir "%winbuild%\deep_3d_photo"

cd "%winbuild%"
git clone --recurse-submodules --depth 1 --shallow-submodules https://github.com/Mulugruntz/deep_3d_photo.git -b windows_build "%winbuild%\deep_3d_photo"


SET COMMAND=dir /b /s "%build_tools%\Winpython*.exe"
FOR /F "delims=" %%A IN ('%COMMAND%') DO (
    SET WPYTHON_EXE=%%A
    GOTO :Out
)

:Out

"%WPYTHON_EXE%" -y -o"%winbuild%\wpython"

setlocal EnableDelayedExpansion
set multiLine=from pathlib import Path ^

import shutil ^

source = str(next(next((Path(r'%winbuild%').resolve() / 'wpython').glob(r'WPy*')).glob(r'python*'))) ^

dest = str(Path(r'%winbuild%').resolve() / 'deep_3d_photo' / 'python38') ^

print(f'''Moving '{source}' to '{dest}' ''')  ^

shutil.move(source, dest) ^

shutil.rmtree(Path(r'%winbuild%').resolve() / 'wpython')

echo !multiLine!

python -c "!multiLine!"

"%winbuild%\deep_3d_photo\python38\python.exe" -m pip install --upgrade pip
"%winbuild%\deep_3d_photo\python38\python.exe" -m pip install pipenv

xcopy "%build_tools%\START.bat" "%winbuild%"
rmdir /s /q "%winbuild%\deep_3d_photo\.git"
rmdir /s /q "%winbuild%\deep_3d_photo\build_tools"
del /q "%winbuild%\deep_3d_photo\.gitignore"
del /q "%winbuild%\deep_3d_photo\.gitmodules"
del /q "%winbuild%\deep_3d_photo\3d-photo-inpainting\depth\*"
del /q "%winbuild%\deep_3d_photo\3d-photo-inpainting\video\*"
