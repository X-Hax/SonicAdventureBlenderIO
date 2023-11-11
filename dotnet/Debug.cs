using SA3D.Modeling.ModelData;
using SA3D.Modeling.ObjectData;
using System.Text.Json;

namespace SA3D.Modeling.Blender
{
    public struct DebugModel
    {
        public NodeStruct[] Nodes { get; set; }
        public MeshStruct[] WeightedAttaches { get; set; }
        public AttachFormat Format { get; set; }
        public bool Optimize { get; set; }
        public bool IgnoreWeights { get; set; }
        public bool IgnoreRoot { get; set; }
        public bool WriteSpecular { get; set; }
        public bool AutoNodeAttributes { get; set; }

        public DebugModel(NodeStruct[] nodes, MeshStruct[] weightedAttaches, AttachFormat format, bool optimize, bool ignoreWeights, bool ignoreRoot, bool writeSpecular, bool autoNodeAttributes)
        {
            Nodes = nodes;
            WeightedAttaches = weightedAttaches;
            Format = format;
            Optimize = optimize;
            IgnoreWeights = ignoreWeights;
            IgnoreRoot = ignoreRoot;
            WriteSpecular = writeSpecular;
            AutoNodeAttributes = autoNodeAttributes;
        }

        public void ToFile(string filename)
            => File.WriteAllText(filename, JsonSerializer.Serialize(this, Structs.Json.JsonConverters.GetOptions()));

        public static DebugModel FromFile(string filename)
            => JsonSerializer.Deserialize<DebugModel>(File.ReadAllText(filename), Structs.Json.JsonConverters.GetOptions());

        public Node ToNodeStructure()
        {
            return Model.ToNodeStructure(
                Nodes,
                WeightedAttaches,
                Format,
                Optimize,
                IgnoreWeights,
                IgnoreRoot,
                WriteSpecular,
                AutoNodeAttributes);
        }
    }
}
