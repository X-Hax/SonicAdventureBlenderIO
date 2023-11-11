using SA3D.Common;
using SA3D.Ini;
using SA3D.Ini.Converters;
using SA3D.Modeling.Structs;
using System.ComponentModel;
using System.Numerics;

namespace SAIO.NET
{
    public class CurvePath
    {
        public static PathData FromPoints(Vector3[] positions, Vector3[] normals)
        {
            PathData result = new();

            for(int i = 0; i < positions.Length; i++)
            {
                Vector3 xyAngles = normals[i].NormalToXZAngles();

                PathDataEntry entry = new()
                {
                    Position = positions[i],
                    XRotation = xyAngles.X,
                    ZRotation = xyAngles.Z
                };

                if(i < positions.Length - 1)
                {
                    entry.Distance = Vector3.Distance(entry.Position, positions[i + 1]);
                    result.TotalDistance += entry.Distance;
                }

                result.Path.Add(entry);
            }

            return result;
        }

        public static (Vector3[] positions, Vector3[] normals) ToPoints(PathData path)
        {
            Vector3[] positions = new Vector3[path.Path.Count];
            Vector3[] normals = new Vector3[positions.Length];

            for(int i = 0; i < positions.Length; i++)
            {
                PathDataEntry entry = path.Path[i];
                positions[i] = entry.Position;
                normals[i] = Vector3Extensions.XZAnglesToNormal(new(entry.XRotation, 0, entry.ZRotation));
            }

            return (positions, normals);
        }
    }

    public class PathData
    {
        public short Unknown { get; set; }

        public float TotalDistance { get; set; }

        [IniCollection(IniCollectionMode.IndexOnly)]
        public List<PathDataEntry> Path { get; set; }

        [TypeConverter(typeof(UInt32HexConverter))]
        public uint Code { get; set; }

        public PathData()
        {
            Path = new();
        }

        public static PathData ReadINIFile(string filename)
        {
            return IniDeserialize.Deserialize<PathData>(filename)
                ?? throw new InvalidOperationException($"Failed to parse file {filename} to pathdata!");
        }

        public void WriteINIFile(string filename)
        {
            IniSerialize.Serialize(this, filename);
        }

        public static PathData Read(IByteData data, uint address)
        {
            PathData result = new()
            {
                Unknown = data.GetInt16(address),
                TotalDistance = data.GetSingle(address + 4)
            };

            ushort count = data.GetUInt16(address + 2);
            if(data.GetPointer(address + 8, out uint entryAddr))
            {
                for(int i = 0; i < count; i++)
                {
                    result.Path.Add(PathDataEntry.Read(data, entryAddr));
                    entryAddr += PathDataEntry.Size;
                }
            }

            return result;
        }

        public void Write(EndianWriter writer)
        {
            uint pathAddr = writer.PointerPosition;
            foreach(PathDataEntry entry in Path)
            {
                entry.Write(writer);
            }

            writer.WriteInt16(Unknown);
            writer.WriteUInt16((ushort)Path.Count);
            writer.WriteSingle(TotalDistance);
            writer.WriteUInt32(pathAddr);
        }

        public void ToCode(string name, bool usePathStructs, out string entries, out string head)
        {
            string arrayType;
            string arrayName;
            string headType;
            string headName;

            if(usePathStructs)
            {
                arrayType = "pathtbl";
                arrayName = $"pathtbl_{name}";
                headType = "pathtag";
                headName = $"pathtag_{name}";
            }
            else
            {
                arrayType = "Loop";
                arrayName = $"{name}_entries";
                headType = "LoopHead";
                headName = name;
            }

            entries = $"{arrayType} {arrayName}[] = {{";
            foreach(PathDataEntry entry in Path)
            {
                entries += $"\n\t{entry.ToStruct(usePathStructs)},";
            }

            if(Path.Count > 0)
            {
                // removing last comma
                entries = entries[..^1];
            }

            entries += "\n};";
            var floatToString = IOType.Float.GetFloatPrinter();

            head = $"{headType} {headName} = {{ {Unknown}, LengthOfArray<int16_t>({arrayName}), {floatToString(TotalDistance)}, {arrayName}, (ObjectFuncPtr)0x{Code:X} }};";
        }

        public void ToCodeFile(string filepath, bool usePathStructs)
        {
            string name = System.IO.Path.GetFileNameWithoutExtension(filepath).Replace('.', '_');
            ToCode(name, usePathStructs, out string entries, out string head);

            string filetext = entries + "\n\n" + head;
            File.WriteAllText(filepath, filetext);
        }
    }

    [Serializable]
    public class PathDataEntry
    {
        public const int Size = 20;

        [TypeConverter(typeof(BAMS16Converter))]
        public float XRotation { get; set; }

        [TypeConverter(typeof(BAMS16Converter))]
        public float ZRotation { get; set; }

        public float Distance { get; set; }

        [TypeConverter(typeof(Vector3Converter))]
        public Vector3 Position { get; set; }

        public PathDataEntry() { }

        public static PathDataEntry Read(IByteData data, uint address)
        {
            return new()
            {
                XRotation = MathHelper.BAMSToRad(data.GetUInt16(address)),
                ZRotation = MathHelper.BAMSToRad(data.GetUInt16(address + 2)),
                Distance = data.GetSingle(address + 4),
                Position = data.ReadVector3(address + 8)
            };
        }

        public void Write(EndianWriter writer)
        {
            writer.WriteUInt16((ushort)MathHelper.RadToBAMS(XRotation));
            writer.WriteUInt16((ushort)MathHelper.RadToBAMS(ZRotation));
            writer.WriteSingle(Distance);
            Position.Write(writer);
        }

        public string ToStruct(bool usePathStructs)
        {
            var bamsToString = IOType.BAMS16.GetFloatPrinter();
            var floatToString = IOType.Float.GetFloatPrinter();

            string positionStruct = Position.ToStruct();
            if(usePathStructs)
            {
                // removing the curly brackets
                positionStruct = positionStruct[2..^2];
            }

            return $"{{ {bamsToString(XRotation)}, {bamsToString(ZRotation)}, {floatToString(Distance)}, {positionStruct} }}";
        }
    }
}
