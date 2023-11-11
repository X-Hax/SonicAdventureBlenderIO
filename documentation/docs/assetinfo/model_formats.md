# Model formats

There are 3 different model formats utilized between the adventure games, each with its own strenghts and limitations. This page gives a rough overview over how every format behaves.

## SA1 - "BASIC"
Titled the BASIC format, it was first used in SA1 and later reused for SA2, albeit only for collision models.

BASIC Models are as simple as it can get, but are able to store all relevant vertex information at once: Normals, Vertex colors, UVs, even polygon normals. It has the simplest material setup, storing all relevant info in one big structure.

Unfortunately, it does not properly support weighted models. SADX relied on "welding", a technique where triangles were drawn between multiple individual models, to achieve connected character models.

## SA2 - "CHUNK"
The Chunk format was introduced in SA2 and is a rather unconventional format.

Chunk models allow for storing vertices in many different combination, but SA2 only supports 3 of them:

- Normals
- Normals & Weights
- Colors

This means that you cannot combine shading with overlaid vertex colors, like SA1 did.

The chunk model also utilizes, fittingly named, "chunks": Mesh data is split up into multiple blocks, each serving its own purpose, like Texture Chunks, Material Chunks and Polygon Chunks. Models then give a sequence of these chunks, which the game processes in order. Several models in SA2 require a very specific order of chunks to function properly, like the chao models (which the addon supports) and the Chaos 0 model (requires extensive technical knowledge to replace).

Weighted chunk models also dont store the mesh as a whole, but divide them up among nodes. Every node stores vertices relative to themselve, which makes processing them in order easier, but takes more space and comes with the caveat of models having no "default" pose.

## SA2B - GC
Simply named the "Gamecube" format (but also called "Ginja"), as it first appeared in the Gamecube port of SA2. It is basically a gamecube formatted model with some modifications to suit SA2 specifically. It was taken over as is to later ports.

The format is very similar to the BASIC format, but doesnt not allow combining Normals and Colors. It does not support weighted models.

## Summary

- SA1 "BASIC"
	- Allows for storing all vertex data
	- No weighted models
	- (almost) Everything in SA1, collisions in SA2
- SA2 "CHUNK"
	- Allow for weights
	- Cannot combine normals and colors
	- Unconventional storage, optimized for processing time
- SA2B "GC"
	- Mostly formated as a Gamecube model
	- Does not support combining Normals and Vertex Colors
	- No weighted models