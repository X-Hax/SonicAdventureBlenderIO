# Mesh Properties
![](../../img/ui_mesh_properties.png){ align=right }

Mesh related properties.

<br clear="right"/>

---

### Force vertex colors
If you have a model with multiple vertex weights the addon will export it with normals, regardless of whether it has color attributes or not. This is because the SA2 mesh format doesn't allow for smooth weights and vertex colors to be combined (or rather, the games do not support it).

Forcing vertex colors will export the model with binary weights (each vertex will be tied to a specific bone) to keep the vertex colors on it.