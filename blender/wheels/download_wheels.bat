@echo off

pushd ..\.venv\Scripts
set py=%CD%\python.exe
popd

IF EXIST %py% (
	%py% -m pip install --upgrade pip

	%py% -m pip download colorama
) ELSE (
	echo Virtual environment not set up. aborting
)