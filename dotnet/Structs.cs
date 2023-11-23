using SA3D.Modeling.Mesh;
using SA3D.Modeling.Mesh.Buffer;
using SA3D.Modeling.Mesh.Weighted;
using SA3D.Modeling.ObjectData;
using SA3D.Modeling.ObjectData.Enums;
using SA3D.Modeling.Structs;
using System.Numerics;


namespace SAIO.NET
{
    public struct NodeStruct
    {
        public string Label { get; set; }
        public Matrix4x4 WorldMatrix { get; set; }
        public int ParentIndex { get; set; }
        public NodeAttributes Attributes { get; set; }

        public NodeStruct(string label, int parentIndex, NodeAttributes attributes, Matrix4x4 worldMatrix)
        {
            Label = label;
            ParentIndex = parentIndex;
            Attributes = attributes;
            WorldMatrix = worldMatrix;
        }
    }

    public struct LandEntryStruct
    {
        public string Label { get; set; }
        public int MeshIndex { get; set; }
        public uint BlockBit { get; set; }
        public Matrix4x4 WorldMatrix { get; set; }
        public NodeAttributes NodeAttributes { get; set; }
        public SurfaceAttributes SurfaceAttributes { get; set; }

        public LandEntryStruct(string label, int meshIndex, uint blockBit, NodeAttributes nodeAttributes, SurfaceAttributes surfaceAttributes, Matrix4x4 worldMatrix)
        {
            Label = label;
            MeshIndex = meshIndex;
            BlockBit = blockBit;
            WorldMatrix = worldMatrix;
            NodeAttributes = nodeAttributes;
            SurfaceAttributes = surfaceAttributes;
        }


        public LandEntry ToLandEntry(Attach attach, bool automaticNodeAttributes)
        {
            Matrix4x4.Decompose(WorldMatrix, out Vector3 scale, out Quaternion rotation, out Vector3 position);
            Vector3 euler = rotation.QuaternionToEuler(NodeAttributes.HasFlag(NodeAttributes.RotateZYX));

            LandEntry result = LandEntry.CreateWithAttach(attach, SurfaceAttributes);
            result.BlockBit = BlockBit;

            result.Model.Label = Label;
            result.Model.SetAllNodeAttributes(NodeAttributes);
            result.Model.Position = position;
            result.Model.EulerRotation = euler;
            result.Model.Scale = scale;

            if(automaticNodeAttributes)
            {
                result.Model.AutoNodeAttributes();
            }

            return result;
        }
    }

    public struct MeshStruct
    {
        public string Label { get; set; }
        public WeightedVertex[] Vertices { get; set; }
        public BufferCorner[][] Corners { get; set; }
        public BufferMaterial[] Materials { get; set; }
        public int RootNodeIndex { get; set; }
        public bool HasVertexColors { get; set; }
        public bool ForceVertexColors { get; set; }

        public MeshStruct(
            string label,
            WeightedVertex[] vertices,
            BufferCorner[][] corners,
            BufferMaterial[] materials,
            int rootNodeIndex,
            bool hasVertexColors,
            bool forceVertexColors)
        {
            Label = label;
            Vertices = vertices;
            Corners = corners;
            Materials = materials;
            RootNodeIndex = rootNodeIndex;
            HasVertexColors = hasVertexColors;
            ForceVertexColors = forceVertexColors;
        }

        public WeightedMesh ToWeightedBuffer(bool writeSpecular)
        {
            WeightedMesh wba = WeightedMesh.Create(Vertices, Corners, Materials, HasVertexColors);

            wba.Label = Label;
            wba.RootIndices.Add(RootNodeIndex);
            wba.ForceVertexColors = ForceVertexColors;
            wba.WriteSpecular = writeSpecular;

            return wba;
        }
    }

}
