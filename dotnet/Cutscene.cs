using SA3D.Modeling.Mesh.Chunk;
using SA3D.Modeling.Mesh.Chunk.PolyChunks;
using SA3D.Modeling.ObjectData;
using SA3D.SA2Event;
using SA3D.SA2Event.Model;
using SA3D.Texturing;
using SA3D.Texturing.Texname;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace SAIO.NET
{
    public class Cutscene
    {
        public Model[] Models { get; }

        public Node[] NotArmaturedModels { get; }

        public ModelData EventData { get; }

        public TextureSet? Textures { get; }

        public TextureNameList? TexNames { get; }

        public Cutscene(Model[] models, Node[] notArmaturedModels, ModelData eventData, TextureSet? textures, TextureNameList? texNames)
        {
            Models = models;
            NotArmaturedModels = notArmaturedModels;
            EventData = eventData;
            Textures = textures;
            TexNames = texNames;
        }

        private static void NameObjects(string basename, ModelData modeldata)
        {
            static void NameHierarchy(string name, Node? root)
            {
                if(root == null)
                {
                    return;
                }

                Node[] nodes = root.GetTreeNodes();

                if(nodes.Length == 1)
                {
                    nodes[0].Label = name;
                }
                else
                {
                    for(int i = 0; i < nodes.Length; i++)
                    {
                        nodes[i].Label = $"{name}_{i:D3}";
                    }
                }

            }

            int entryIndex = 0;
            foreach(EventEntry entry in modeldata.Scenes[0].Entries)
            {
                NameHierarchy($"{basename}_{entryIndex++:D3}", entry.DisplayModel);
            }

            for(int i = 0; i < modeldata.OverlayUpgrades.Length; i++)
            {
                OverlayUpgrade upgrade = modeldata.OverlayUpgrades[i];

                NameHierarchy($"{basename}_upgrade_{i:D2}_m1", upgrade.Model1);
                NameHierarchy($"{basename}_upgrade_{i:D2}_m2", upgrade.Model2);
            }

            HashSet<Node> commons = new();
            List<Node> commonsOrdered = new();
            HashSet<Node> iterated = new();

            Dictionary<Node, Node> shadowModels = new();

            foreach(Scene scene in modeldata.Scenes.Skip(1))
            {
                foreach(EventEntry entry in scene.Entries)
                {
                    if(!iterated.Contains(entry.DisplayModel))
                    {
                        iterated.Add(entry.DisplayModel);
                        if(entry.ShadowModel != null)
                        {
                            shadowModels.Add(entry.DisplayModel, entry.ShadowModel);
                        }
                    }
                    else if(!commons.Contains(entry.DisplayModel))
                    {
                        commons.Add(entry.DisplayModel);
                        commonsOrdered.Add(entry.DisplayModel);
                    }
                }
            }

            for(int i = 0; i < commonsOrdered.Count; i++)
            {
                NameHierarchy($"{basename}_common_{i:D3}", commonsOrdered[i]);
            }

            for(int i = 1; i < modeldata.Scenes.Count; i++)
            {
                int index = 0;
                foreach(EventEntry entry in modeldata.Scenes[i].Entries)
                {
                    if(commons.Contains(entry.DisplayModel))
                    {
                        continue;
                    }

                    NameHierarchy($"{basename}_{i:D2}_{index:D3}", entry.DisplayModel);

                    index++;
                }
            }

            foreach(KeyValuePair<Node, Node> item in shadowModels)
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

            if(File.Exists(texturePath))
            {
                try
                {
                    textures = SA3D.Archival.Archive.ReadArchiveFromFile(texturePath).ToTextureSet();
                }
                catch { }
            }


            Event eventData = Event.ReadFromFiles(path);
            NameObjects(Path.GetFileNameWithoutExtension(path), eventData.ModelData);

            HashSet<Node> nodes = eventData.ModelData.GetModels(true);


            List<Model> models = new();
            foreach(Node node in nodes)
            {
                models.Add(Model.Process(node, null, optimize));
            }

            // compare texture list with texture names
            TextureNameList? texNames = null;
            if(eventData.ExternalTexlist != null)
            {
                if(textures == null || eventData.ExternalTexlist.TextureNames.Length != textures.Textures.Count)
                {
                    texNames = eventData.ExternalTexlist;
                }
                else
                {
                    for(int i = 0; i < textures.Textures.Count; i++)
                    {
                        TextureName name = eventData.ExternalTexlist.TextureNames[i];
                        SA3D.Texturing.Texture texture = textures.Textures[i];
                        if(name.Name?.Trim().ToLower() != texture.Name.Trim().ToLower())
                        {
                            texNames = eventData.ExternalTexlist;
                            break;
                        }
                    }
                }
            }

            return new(
                models.ToArray(),
                eventData.ModelData.GetNonAnimatedModels(true).ToArray(),
                eventData.ModelData,
                textures,
                texNames);
        }

        public static int GetMaterialIndex(Node model, TextureChunk textureChunk)
        {
            if(model.Attach == null)
            {
                throw new InvalidOperationException("Model has no attach");
            }

            Dictionary<ChunkAttach, PolyChunk?[]> activePolychunks = ChunkAttach.GetActivePolyChunks(model);

            if(!activePolychunks.TryGetValue((ChunkAttach)model.Attach, out PolyChunk?[]? polychunks))
            {
                throw new InvalidOperationException("model has no active poly chunks");
            }

            int materialIndex = 0;
            TextureChunk? curID = null;

            foreach(PolyChunk? cnk in polychunks)
            {
                switch(cnk)
                {
                    case TextureChunk texChunk:
                        curID = texChunk;
                        break;
                    case StripChunk:
                        if(curID == textureChunk)
                        {
                            return materialIndex;
                        }

                        materialIndex++;
                        break;
                }
            }

            throw new InvalidOperationException("Material index not found. Texture chunk not part of the (rendered) attaches");
        }

        public static TextureChunk GetTextureChunkFromMaterialIndex(Node model, int materialIndex)
        {
            if(model.Attach == null)
            {
                throw new InvalidOperationException("Model has no attach");
            }

            Dictionary<ChunkAttach, PolyChunk?[]> activePolychunks = ChunkAttach.GetActivePolyChunks(model);

            if(!activePolychunks.TryGetValue((ChunkAttach)model.Attach, out PolyChunk?[]? polychunks))
            {
                throw new InvalidOperationException("model has no active poly chunks");
            }

            int currentMaterialIndex = 0;
            TextureChunk? curID = null;

            foreach(PolyChunk? cnk in polychunks)
            {
                switch(cnk)
                {
                    case TextureChunk texChunk:
                        curID = texChunk;
                        break;
                    case StripChunk:
                        if(currentMaterialIndex == materialIndex)
                        {
                            return curID ?? throw new InvalidOperationException("No texture id chunk found");
                        }

                        currentMaterialIndex++;
                        break;
                }

            }

            throw new InvalidOperationException("No texture chunk found");
        }

    }
}
