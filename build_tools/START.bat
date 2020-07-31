SET current=%~dp0
SET current=%current:~0,-1%
cd "%current%\deep_3d_photo"
.venv\Scripts\python.exe main.py -m inspector
pause
