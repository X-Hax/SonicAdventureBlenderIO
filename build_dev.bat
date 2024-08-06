@echo off

move .\blender\blender_manifest.toml .\blender\blender_manifest.prod.toml
move .\blender\blender_manifest.dev.toml .\blender\blender_manifest.toml
move .\blender\__init__.py .\blender\__init__.prod.py
move .\blender\__init__.dev.py .\blender\__init__.py


if exist ".\build" (
	rmdir ".\build" /s /q
)

mkdir .\build
blender --command extension build --source-dir .\blender --output-dir .\build
blender --command extension server-generate --repo-dir=.\build --html

move .\blender\blender_manifest.toml .\blender\blender_manifest.dev.toml
move .\blender\blender_manifest.prod.toml .\blender\blender_manifest.toml
move .\blender\__init__.py .\blender\__init__.dev.py
move .\blender\__init__.prod.py .\blender\__init__.py