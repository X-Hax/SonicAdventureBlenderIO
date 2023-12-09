# Land Entry Properties Panel
![](../../img/ui_landentry_properties.png){ align=right }

In landtable scenes, this panel is used to set level geometry properties and to define how the model behaves during gameplay.

The panel can be found in the **properties editor**, under the **object** tab, called "SAIO Land Entry Properties".

<br clear="right">

---

### Type
There are 2 types of level geometry: Static and Animated.

- **Static** land entries are the regular geometry, and the only one supported by Sonic adventure 2 (and ports)
- **Animated** land entries can be used in Sonic Adventure 1, and allow you to insert animated models into a stage, but without collision or any other additional features.

There are a few rules in place as to which models can be set as `static` and which as `animated`:

- Objects with a parent get their geometry type from their parent.
- Armature models are automatically recognized as `animated`.
- Non-armature objects with children are automatically recognized as `static`.
- The geometry type can only be chosen for objects with no child and no parent.

Additionally, all models recognized as `static` will evaluate as their own geometry object, as levels dont support object hierarchies for static geometry.

---

## Static-type properties

### Surface Attributes
These define how a model is rendered and collided with. Both SA1 and SA2 have different sets of surface attributes to accomodate for different functionalities between the games, but many are shared.

By changing the edit mode (**Universal** by default), you can change which attributes you want to see and edit, making it easier to manage surface attributes for a specific game.

TODO: Document all attributes here

### Blockbit

<figure class="align-right" markdown>
![Blockbitmap for city escape](../../img/ui_blockmap_city_escape.png){ width=256 }
<figcaption>Blockmap for city escape</figcaption>
</figure>

This is a hexadecimal [**bitmask**](https://en.wikipedia.org/wiki/Mask_(computing)) that is used by Blockmaps. Blockmaps help the adventure games render larger levels by grouping geometry together in blocks and processing only the geometry associated with the block that the player is currently inside. The blockbit defines which blocks the object is part of, each bit defining a single group (allowing for a total of 32 blocks).

In coding, each bit is assigned a color, which are then used in a blockmap image. The game then looks up which pixel in the map the player is located in, and will only process geometry which have set the corresponding bit as the pixels color.

---

## Animated-type properties

### Start Frame Offset
This property is actually used by the game to store the current animation time.
<br/> By setting it to a custom value, you can make the object start playing the animation at an offset.
<br/> This allows you to reuse the same animation between multiple objects, without having them play in sync.

### Speed
Animation playback speed

### Texlist pointer
Pointer to the texture list to use. Leaving a `0` will make it use the landtable textures.