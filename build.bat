@echo off

if exist ".\build" (
	rmdir "./build" /s /q
)

mkdir ".\build"
mkdir ".\build\SonicAdventureBlenderIO"
mkdir ".\build\SonicAdventureBlenderIO\DLL"
mkdir ".\build\SonicAdventureBlenderIO\source"

copy ".\blender\__init__.py" ".\build\SonicAdventureBlenderIO\__init__.py"
copy ".\blender\SAIOTemplates.blend" ".\build\SonicAdventureBlenderIO\SAIOTemplates.blend"
copy ".\blender\DLL" ".\build\SonicAdventureBlenderIO\DLL"
robocopy ".\blender\source" ".\build\SonicAdventureBlenderIO\source" /s /xd __pycache__

pushd ".\build"
tar -acf SonicAdventureBlenderIO.zip SonicAdventureBlenderIO
popd