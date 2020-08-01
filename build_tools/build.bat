SET build_tools=%~dp0
SET build_tools=%build_tools:~0,-1%
SET winbuild=%build_tools%\..\winbuild

if exist "%winbuild%" rmdir /s /q "%winbuild%"
mkdir "%winbuild%\deep_3d_photo"
mkdir "%winbuild%\venv"

cd "%winbuild%\venv"
SET PIPENV_VENV_IN_PROJECT=1
SET PIPENV_NO_INHERIT=1
python -m pipenv install --site-packages --python 3.8 --skip-lock
python -m pipenv install pipenv --skip-lock

cd "%winbuild%"
git clone --recurse-submodules --depth 1 --shallow-submodules https://github.com/Mulugruntz/deep_3d_photo.git -b windows_build "%winbuild%\deep_3d_photo"

move "%winbuild%\venv\.venv" "%winbuild%\deep_3d_photo\bootstrap"
rmdir /s /q "%winbuild%\venv"
xcopy "%build_tools%\START.bat" "%winbuild%"
rmdir /s /q "%winbuild%\deep_3d_photo\.git"
rmdir /s /q "%winbuild%\deep_3d_photo\build_tools"
del /q "%winbuild%\deep_3d_photo\.gitignore"
del /q "%winbuild%\deep_3d_photo\.gitmodules"
del /q "%winbuild%\deep_3d_photo\3d-photo-inpainting\depth\*"
del /q "%winbuild%\deep_3d_photo\3d-photo-inpainting\video\*"
