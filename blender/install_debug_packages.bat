@echo off
echo installing python packages so that debugging works
cd %~dp0

IF NOT EXIST .\.venv\pyvenv.cfg (
	echo Please set up the virtual python environment first!
	exit /b 1
)

for /f "tokens=2*" %%a in ('FINDSTR /b "executable = " .\.venv\pyvenv.cfg') do (
	set python=%%b
)

set target=%APPDATA%\Blender Foundation\Blender\4.2\extensions\.local\lib\python3.11\site-packages

"%python%" -m pip install debugpy --target "%target%"
"%python%" -m pip install requests --target "%target%"
"%python%" -m pip install flask --target "%target%"
"%python%" -m pip install pythonnet --target "%target%"