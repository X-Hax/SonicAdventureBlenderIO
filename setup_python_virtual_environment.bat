@echo off
echo Setting up python virtual environment for the project
cd %~dp0

rem getting the python path
set /P python=Enter Blender Python Path:
echo %python%
IF EXIST %python% (
	echo Python found

	rem creating the virtual environment
	%python% -m venv .venv
	cd .venv\Scripts

	rem first, we gotta upgrade pip
	python.exe -m pip install --upgrade pip

	rem now install the packages
	pip.exe install pep8
	pip.exe install autopep8
	pip.exe install pycodestyle
	pip.exe install pylint
	pip.exe install pythonnet
	pip.exe install fake-bpy-module-3.4

	echo set up!

) ELSE (
	echo Python path not valid. aborting
)
