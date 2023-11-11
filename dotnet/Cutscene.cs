using SA3D.Archival.Tex;
using SA3D.Event.SA2.Model;
using SA3D.Modeling.ModelData.CHUNK;
using SA3D.Modeling.ModelData.Weighted;
using SA3D.Modeling.ObjectData;
using SA3D.Texturing;
using SA3D.Texturing.NJS;

namespace SA3D.Modeling.Blender
{
    public class Cutscene
    {
        public Model[] Models { get; }

        public Node[] NotArmaturedModels { get; }

        public Event.SA2.Model.ModelData EventData { get; }

        public TextureSet? Textures { get; }

        public NjsTexList? TexNames { get; }

        public Cutscene(Model[] models, Node[] notArmaturedModels, Event.SA2.Model.ModelData eventData, TextureSet? textures, NjsTexList? texNames)
        {
            Models = models;
            NotArmaturedModels = notArmaturedModels;
            EventData = eventData;
            Textures = textures;
            TexNames = texNames;
        }

        private static void NameObjects(string basename, Event.SA2.Model.ModelData modeldata)
        {
            static void NameHierarchy(string name, Node? root)
            {
                if (root == null)
                    return;

                Node[] nodes = root.GetNodes();

                if (nodes.Length == 1)
                {
                    nodes[0].Label = name;
                }
                else
                {
                    for (int i = 0; i < nodes.Length; i++)
                    {
                        nodes[i].Label = $"{name}_{i:D3}";
                    }
                }

            }

            int entryIndex = 0;
            foreach (EventEntry entry in modeldata.Scenes[0].Entries)
            {
                NameHierarchy($"{basename}_{entryIndex++:D3}", entry.DisplayModel);
            }

            for (int i = 0; i < modeldata.Upgrades.Length; i++)
            {
                var upgrade = modeldata.Upgrades[i];

                NameHierarchy($"{basename}_upgrade_{i:D2}_m1", upgrade.Model1);
                NameHierarchy($"{basename}_upgrade_{i:D2}_m2", upgrade.Model2);
            }

            HashSet<Node> commons = new();
            List<Node> commonsOrdered = new();
            HashSet<Node> iterated = new();

            Dictionary<Node, Node> shadowModels = new();

            foreach (Scene scene in modeldata.Scenes.Skip(1))
            {
                foreach (EventEntry entry in scene.Entries)
                {
                    if (!iterated.Contains(entry.DisplayModel))
                    {
                        iterated.Add(entry.DisplayModel);
                        if(entry.ShadowModel != null)
                        {
                            shadowModels.Add(entry.DisplayModel, entry.ShadowModel);
                        }
                    }
                    else if (!commons.Contains(entry.DisplayModel))
                    {
                        commons.Add(entry.DisplayModel);
                        commonsOrdered.Add(entry.DisplayModel);
                    }
                }
            }

            for (int i = 0; i < commonsOrdered.Count; i++)
            {
                NameHierarchy($"{basename}_common_{i:D3}", commonsOrdered[i]);
            }

            for (int i = 1; i < modeldata.Scenes.Count; i++)
            {
                int index = 0;
                foreach (EventEntry entry in modeldata.Scenes[i].Entries)
                {
                    if (commons.Contains(entry.DisplayModel))
                        continue;

                    NameHierarchy($"{basename}_{i:D2}_{index:D3}", entry.DisplayModel);
                    
                    index++;
                }
            }

            foreach (KeyValuePair<Node, Node> item in shadowModels)
            {
                string name = item.Key.Label[..^4];
                NameHierarchy(name + "_shadow", item.Value);
            }
        }

        public static Cutscene Import(string path, bool optimize)
        {
            string texturePath = Path.Join(
                Path.GetDirectoryName(path),
                Path.GetFileNameWithoutExtension(path) + "texture.prs");

            TextureSet? textures = null;

            if (File.Exists(texturePath))
            {
                try
                {
                    textures = TextureArchive.ReadArchiveFromFile(texturePath).ToTextureSet();
                }
                catch { }
            }


            Event.SA2.Event eventData = Event.SA2.Event.ReadFiles(path);
            NameObjects(Path.GetFileNameWithoutExtension(path), eventData.MainData);

            Node[] nodes = eventData.MainData.GetModels(true);


            List<Model> models = new();
            foreach (Node node in nodes)
            {
                models.Add(Model.Process(node, optimize));
            }

            // compare texture list with texture names
            NjsTexList? texNames = null;
            if(eventData.ExternalTexlist != null)
            {
                if (textures == null || eventData.ExternalTexlist.TextureNames.Length != textures.Textures.Count)
                {
                    texNames = eventData.ExternalTexlist;
                }
                else
                {
                    for (int i = 0; i < textures.Textures.Count; i++)
                    {
                        var name = eventData.ExternalTexlist.TextureNames[i];
                        var texture = textures.Textures[i];
                        if (name.Name?.Trim().ToLower() != texture.Name.Trim().ToLower())
                        {
                            texNames = eventData.ExternalTexlist;
                            break;
                        }
                    }
                }
            }

            return new(
                models.ToArray(),
                eventData.MainData.GetNonAnimatedModels(true),
                eventData.MainData,
                textures,
                texNames);
        }

        public static int GetMaterialIndex(Node model, PolyChunkTextureID textureChunk)
        {
            if (model.Attach == null)
                throw new InvalidOperationException("Model has no attach");

            Dictionary<ChunkAttach, PolyChunk[]> activePolychunks = ChunkAttachConverter.GetActivePolyChunks(model.RootParent);

            if (!activePolychunks.TryGetValue((ChunkAttach)model.Attach, out PolyChunk[]? polychunks))
                throw new InvalidOperationException("model has no active poly chunks");

            int materialIndex = 0;
            PolyChunkTextureID? curID = null;

            foreach (PolyChunk cnk in polychunks)
            {
                switch (cnk.Type)
                {
                    case ChunkType.Tiny_TextureID:
                    case ChunkType.Tiny_TextureID2:
                        curID = (PolyChunkTextureID)cnk;
                        break;
                    case ChunkType.Strip_Strip:
                    case ChunkType.Strip_StripUVN:
                    case ChunkType.Strip_StripUVH:
                    case ChunkType.Strip_StripNormal:
                    case ChunkType.Strip_StripUVNNormal:
                    case ChunkType.Strip_StripUVHNormal:
                    case ChunkType.Strip_StripColor:
                    case ChunkType.Strip_StripUVNColor:
                    case ChunkType.Strip_StripUVHColor:
                    case ChunkType.Strip_Strip2:
                    case ChunkType.Strip_StripUVN2:
                    case ChunkType.Strip_StripUVH2:
                        if (curID == textureChunk)
                            return materialIndex;
                        materialIndex++;
                        break;
                }
            }

            throw new InvalidOperationException("Material index not found. Texture chunk not part of the (rendered) attaches");
        }

        public static PolyChunkTextureID GetTextureChunkFromMaterialIndex(Node model, int materialIndex)
        {
            if (model.Attach == null)
                throw new InvalidOperationException("Model has no attach");

            Dictionary<ChunkAttach, PolyChunk[]> activePolychunks = ChunkAttachConverter.GetActivePolyChunks(model.RootParent);

            if (!activePolychunks.TryGetValue((ChunkAttach)model.Attach, out PolyChunk[]? polychunks))
                throw new InvalidOperationException("model has no active poly chunks");

            int currentMaterialIndex = 0;
            PolyChunkTextureID? curID = null;

            foreach (PolyChunk cnk in polychunks)
            {
                switch (cnk.Type)
                {
                    case ChunkType.Tiny_TextureID:
                    case ChunkType.Tiny_TextureID2:
                        curID = (PolyChunkTextureID)cnk;
                        break;
                    case ChunkType.Strip_Strip:
                    case ChunkType.Strip_StripUVN:
                    case ChunkType.Strip_StripUVH:
                    case ChunkType.Strip_StripNormal:
                    case ChunkType.Strip_StripUVNNormal:
                    case ChunkType.Strip_StripUVHNormal:
                    case ChunkType.Strip_StripColor:
                    case ChunkType.Strip_StripUVNColor:
                    case ChunkType.Strip_StripUVHColor:
                    case ChunkType.Strip_Strip2:
                    case ChunkType.Strip_StripUVN2:
                    case ChunkType.Strip_StripUVH2:
                        if (currentMaterialIndex == materialIndex)
                        {
                            if (curID == null)
                                throw new InvalidOperationException("No texture id chunk found");
                            return curID;
                        }
                        currentMaterialIndex++;
                        break;
                }
            }

            throw new InvalidOperationException("No texture chunk found");
        }
    
    }
}
