SET build_tools=%~dp0
SET build_tools=%build_tools:~0,-1%
SET winbuild=%build_tools%\..\winbuild
SET windist=%build_tools%\..\windist

cd "%winbuild%\deep_3d_photo"

for /f %%i in ('.venv\Scripts\python.exe -c "import __version__ as v;print(v.__version__)"') do set VERSION=%%i
ECHO "Version = %VERSION%"

cd "%windist%"
"%build_tools%\inno\ISCC.exe" "%build_tools%\inno_script.iss"
