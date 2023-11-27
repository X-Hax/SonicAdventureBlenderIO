# File Types

These formats originate from either the Sonic adventure games directly or are storage mediums brought into existence by SATools.

---

## Models
Stored in file ending with `*.*mdl`.

- `*.sa1mdl` - Ninja Basic Format Models.
	- Mostly used in SA1 & SADX.
- `*.sa2mdl` - Ninja Chunk Format.
	- Mostly used in SA2 & SA2B, features vertex weights.
	- SADX uses this for Chao and Cream.
- `*.sa2bmdl` - Ginja Chunk Format.
	- Only seen in SA2B.

---

## Stages
Stages are stored in files ending with `*.*lvl`.

- `*.sa1lvl`
	- Used in SA1 & SADX.
- `*.sa2lvl`
	- Used in SA2.
	- Stores collision in Ninja Basic format, separated by collections on import.
- `*.sa2blvl`
	- Used in SA2B/PC.
	- Stores collision in Ninja Basic format, separated by collections on import.
	- Can display **real-time shadows**

---

## Textures
Textures are stored in a variety of archive types.

- `*.PVM`
	- Used in SA1, SADX, and SA2. In SA1 and SA2, they will be compressed in PRS files. *(eg. SONIC.PVM)*
- `*.GVM`
	- Used in SA2B/PC. These are compressed in PRS files. *(eg. sonic-tex.prs)*
- `*.PAK`
	- Used only in SA2PC. These store textures in DDS format. *(eg. adx-logo.pak)*

---

## Animations
Animations are stored in ***.saanim** files

- This format is shared between both games.

## Sonic Adventure 2 Events

SA2 events are a bit more complicated. There are 2 types of Events: Full events, and Mini events.

!!! note
	Event files can be used out of the box from the games resources, and dont need to be extracted with a project.
	<br/> The SATools Project Manager still allows for splitting event files if needed. However, blender is able to handle event files as is.

### Full Events

Full events are almost completely independent of any other game data. All info is stored in multiple files, mostly compressed using PRS.
<br/> Most event related files belonging to the same event all share the same base name, usually a 4 digit number (####*).
<br/> Events mainly consist of the following files:

- `####.prs` - The main event file, containing all 3D models
	- in SA2 for the dreamcast, it also stores animations
- `####_0.prs` - The events effect file, stores information about
	- Default subtitle placements
	- Default audio playback info
	- Screen effects
	- Particle effect information
	- Object Lighting
	- Blare Effect information (unused)
	- Particle emitter information
	- Video Overlays
- `####_%.prs` - These files contain language related information
	- Information contained:
		- Subtitle placements
		- Audio playback info
	- Each file is for a specific language. % denotes the language key:
		- `1`: English
		- `2`: French
		- `3`: Spanish
		- `4`: German
		- `5`: Italian
		- `J`: Japanese
	- These files are **optional**; If not present, the game will use the default information provided by ####_0.prs
- `####texlist.prs` - Texture name list
- `####texture.prs` - Texture archive
	- Compressed **PVM** archive on Dreamcast
	- Compressed **GVM** archive in ports
- `####motion.bin` - Animations
	- Only used in the ports

Blender only requires the following files for importing events:

- `####.prs`
- `####texture.prs`
- `####motion.bin`

---

## Paths
paths are stored in .INI files