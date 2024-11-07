# Migration
This guide will explain how to migrate blender projects created with the old addon to SAIO.

## Background
In 2019, the first version of the **Blender Sonic Adventure Support** addon was released and was used since then to create models for sonic adventure mods. In these 4 years, the addon grew more and more, and unfortunately deteriorated due to inexperience on our behalf.

During the years passed, the SA3D C# API was developed, and it was decided that this should be used to create a new and better addon, faster and better in every way.

A full rewrite was done, and the new addon had several changes that were incompatible with the old addon, but should all be migrateable.

## General migration
To migrate properties of scenes, objects and materials:

1. Got to the [migration panel](../ui/toolbar/tools/migration.md)
2. Click `Check for migrate data`. If your project was created with the old addon, it will find data to migrate and enable the other migrate buttons.
3. Click `Migrate Data`. This should do the job

### Changes between the addons
- Texture lists were moved from the scene to a seperate list panel.
- GC texcoord source for materials was combined.
- Export type for meshes removed; Models now export vertex colors when they have them.
- Armatures no longer count as a node themselves. Root nodes will be added as seperate bones.
- Paths now consist of only a curve

## Armature migration
Armature objects themselves no longer count as the root node, and will instead need to receive a new bone. To do this, simply select the armature and press the "Migrate Armature" button.

## Path Migration
Paths get handled completely different now. To migrate an old path, simply select your old path object and hit "migrate path".

## Update migration
Occasionally we learn more about how the game and model formats work and change certain properties in objects, meshes or materials. When that happens, those properties don't automatically get migrated upon updating the project, and you will have to run the "Update migration" function