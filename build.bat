@echo off

if exist ".\build" (
	rmdir ".\build" /s /q
)

mkdir .\build
blender --command extension build --source-dir .\blender --output-dir .\build
blender --command extension server-generate --repo-dir=.\build --html