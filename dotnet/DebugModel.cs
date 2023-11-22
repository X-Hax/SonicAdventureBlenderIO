using SA3D.Modeling.JSON;
using SA3D.Modeling.Mesh;
using SA3D.Modeling.ObjectData;
using System.IO;
using System.Text.Json;

namespace SAIO.NET
{
    public struct DebugModel
    {
        public NodeStruct[] Nodes { get; set; }
        public MeshStruct[] WeightedAttaches { get; set; }
        public AttachFormat Format { get; set; }
        public bool Optimize { get; set; }
        public bool IgnoreWeights { get; set; }
        public bool WriteSpecular { get; set; }
        public bool AutoNodeAttributes { get; set; }

        public DebugModel(NodeStruct[] nodes, MeshStruct[] weightedAttaches, AttachFormat format, bool optimize, bool ignoreWeights, bool writeSpecular, bool autoNodeAttributes)
        {
            Nodes = nodes;
            WeightedAttaches = weightedAttaches;
            Format = format;
            Optimize = optimize;
            IgnoreWeights = ignoreWeights;
            WriteSpecular = writeSpecular;
            AutoNodeAttributes = autoNodeAttributes;
        }

        public void ToFile(string filename)
        {
            JsonSerializerOptions options = JsonConverters.GetOptions();
            options.ReferenceHandler = new JsonReferenceHandler();

            File.WriteAllText(filename, JsonSerializer.Serialize(this, options));
        }

        public static DebugModel FromFile(string filename)
        {
            JsonSerializerOptions options = JsonConverters.GetOptions();
            options.ReferenceHandler = new JsonReferenceHandler();

            return JsonSerializer.Deserialize<DebugModel>(File.ReadAllText(filename), options);
        }

        public Node ToNodeStructure()
        {
            return Model.ToNodeStructure(
                Nodes,
                WeightedAttaches,
                Format,
                Optimize,
                IgnoreWeights,
                WriteSpecular,
                AutoNodeAttributes);
        }
    }
}
