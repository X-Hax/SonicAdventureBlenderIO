@echo off

if exist ".\build" (
	rmdir "./build" /s /q
)

mkdir ".\build"
mkdir ".\build\SonicAdventureBlenderIO_dev"
mkdir ".\build\SonicAdventureBlenderIO_dev\DLL"
mkdir ".\build\SonicAdventureBlenderIO_dev\source"

copy ".\blender\__init__.py" ".\build\SonicAdventureBlenderIO_dev\__init__.py"
copy ".\blender\SAIOTemplates.blend" ".\build\SonicAdventureBlenderIO_dev\SAIOTemplates.blend"
copy ".\blender\DLL" ".\build\SonicAdventureBlenderIO_dev\DLL"
robocopy ".\blender\source" ".\build\SonicAdventureBlenderIO_dev\source" /s /xd __pycache__

pushd ".\build"
tar -acf SonicAdventureBlenderIO_dev.zip SonicAdventureBlenderIO_dev
popd