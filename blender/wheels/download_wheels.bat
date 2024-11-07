@echo off

pushd ..\.venv\Scripts
set py=%CD%\python.exe
popd

set download=%py% -m pip download pythonnet --only-binary=:all: --platform=
IF EXIST %py% (
	%py% -m pip install --upgrade pip

	%download%win_amd64
	%download%win32

	%download%macosx_10_9_x86_64
	%download%macosx_11_0_arm64

	%download%musllinux_1_1_aarch64
	%download%musllinux_1_1_i686
	%download%musllinux_1_1_x86_64

	%download%manylinux_2_12_i686
	%download%manylinux_2_17_i686
	%download%manylinux_2_17_aarch64
	%download%manylinux_2_17_ppc64le
	%download%manylinux_2_17_s390x
	%download%manylinux_2_17_x86_64

	%download%manylinux2010_i686
	%download%manylinux2014_i686
	%download%manylinux2014_aarch64
	%download%manylinux2014_ppc64le
	%download%manylinux2014_s390x
	%download%manylinux2014_x86_64

) ELSE (
	echo Virtual environment not set up. aborting
)