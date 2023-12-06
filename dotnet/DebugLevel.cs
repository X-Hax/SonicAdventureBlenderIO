using SA3D.Modeling.Animation;
using SA3D.Modeling.JSON;
using SA3D.Modeling.ObjectData;
using SA3D.Modeling.ObjectData.Enums;
using System.IO;
using System.Text.Json;

namespace SAIO.NET
{
    public struct DebugLevel
    {
        public LandEntryStruct[] Landentries { get; set; }
        public MeshStruct[] WeightedAttaches { get; set; }
        public LandEntryMotion[] Motions { get; set; }
        public ModelFormat Format { get; set; }
        public string Name { get; set; }
        public float DrawDistance { get; set; }
        public string TexFileName { get; set; }
        public uint TexListPointer { get; set; }
        public string Filepath { get; set; }
        public bool Optimize { get; set; }
        public bool WriteSpecular { get; set; }
        public bool FallbackSurfaceAttributes { get; set; }
        public bool AutomaticNodeAttributes { get; set; }
        public string Author { get; set; }
        public string Description { get; set; }

        public DebugLevel(LandEntryStruct[] landentries, MeshStruct[] weightedAttaches, LandEntryMotion[] motions, ModelFormat format, string name, float drawDistance, string texFileName, uint texListPointer, string filepath, bool optimize, bool writeSpecular, bool fallbackSurfaceAttributes, bool automaticNodeAttributes, string author, string description)
        {
            Landentries = landentries;
            WeightedAttaches = weightedAttaches;
            Motions = motions;
            Format = format;
            Name = name;
            DrawDistance = drawDistance;
            TexFileName = texFileName;
            TexListPointer = texListPointer;
            Filepath = filepath;
            Optimize = optimize;
            WriteSpecular = writeSpecular;
            FallbackSurfaceAttributes = fallbackSurfaceAttributes;
            AutomaticNodeAttributes = automaticNodeAttributes;
            Author = author;
            Description = description;
        }

        public void ToFile(string filename)
        {
            JsonSerializerOptions options = JsonConverters.GetOptions();
            options.ReferenceHandler = new JsonReferenceHandler();

            File.WriteAllText(filename, JsonSerializer.Serialize(this, options));
        }

        public static DebugLevel FromFile(string filename)
        {
            JsonSerializerOptions options = JsonConverters.GetOptions();
            options.ReferenceHandler = new JsonReferenceHandler();

            return JsonSerializer.Deserialize<DebugLevel>(File.ReadAllText(filename), options);
        }

        public LandTable ToLandtable()
        {
            return LandTableWrapper.ProcessLandtable(
                Landentries,
                WeightedAttaches,
                Motions,
                Format,
                Name,
                DrawDistance,
                TexFileName,
                TexListPointer,
                Optimize,
                WriteSpecular,
                FallbackSurfaceAttributes,
                AutomaticNodeAttributes);
        }
    }
}
