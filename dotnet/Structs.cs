using SA3D.Modeling.ModelData;
using SA3D.Modeling.ModelData.Buffer;
using SA3D.Modeling.ModelData.GC;
using SA3D.Modeling.ModelData.Weighted;
using SA3D.Modeling.ObjectData;
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
        public Matrix4x4 WorldMatrix { get; set; }
        public NodeAttributes NodeAttributes { get; set; }
        public SurfaceAttributes SurfaceAttributes { get; set; }

        public LandEntryStruct(string label, int meshIndex, NodeAttributes nodeAttributes, SurfaceAttributes surfaceAttributes, Matrix4x4 worldMatrix)
        {
            Label = label;
            MeshIndex = meshIndex;
            WorldMatrix = worldMatrix;
            NodeAttributes = nodeAttributes;
            SurfaceAttributes = surfaceAttributes;
        }


        public LandEntry ToLandEntry(Attach attach, bool automaticNodeAttributes)
        {
            Matrix4x4.Decompose(WorldMatrix, out Vector3 scale, out Quaternion rotation, out Vector3 position);
            Vector3 euler = rotation.ToEuler(NodeAttributes.HasFlag(NodeAttributes.RotateZYX));

            LandEntry result = new(attach)
            {
                SurfaceAttributes = SurfaceAttributes
            };

            result.Model.Label = Label;
            result.Model.SetAllNodeAttributes(NodeAttributes);
            result.Model.Position = position;
            result.Model.Rotation = euler;
            result.Model.Scale = scale;

            if(automaticNodeAttributes)
            {
                result.Model.AutoNodeAttributes();
            }

            return result;
        }
    }

    public struct MaterialStruct
    {
        public Color Diffuse { get; set; }
        public Color Specular { get; set; }
        public float SpecularExponent { get; set; }
        public Color Ambient { get; set; }
        public MaterialAttributes MaterialAttributes { get; set; }
        public bool UseAlpha { get; set; }
        public bool Culling { get; set; }
        public BlendMode SourceBlendMode { get; set; }
        public BlendMode DestinationBlendmode { get; set; }
        public uint TextureIndex { get; set; }
        public FilterMode TextureFiltering { get; set; }
        public bool AnisotropicFiltering { get; set; }
        public float MipmapDistanceAdjust { get; set; }
        public bool ClampU { get; set; }
        public bool MirrorU { get; set; }
        public bool ClampV { get; set; }
        public bool MirrorV { get; set; }
        public byte ShadowStencil { get; set; }
        public TexCoordID TexCoordID { get; set; }
        public TexGenType TexGenType { get; set; }
        public TexGenSrc TexGenSrc { get; set; }
        public TexGenMatrix MatrixID { get; set; }

        public MaterialStruct(
            float dr, float dg, float db, float da,
            float sr, float sg, float sb, float sa,
            float specularExponent,
            float ar, float ag, float ab, float aa,
            MaterialAttributes materialAttributes,
            bool useAlpha,
            bool culling,
            BlendMode sourceBlendMode,
            BlendMode destinationBlendmode,
            uint textureIndex,
            FilterMode textureFiltering,
            bool anisotropicFiltering,
            float mipmapDistanceAdjust,
            bool clampU,
            bool mirrorU,
            bool clampV,
            bool mirrorV,
            byte shadowStencil,
            TexCoordID texCoordID,
            TexGenType texGenType,
            TexGenSrc texGenSrc,
            TexGenMatrix matrixID)
        {
            Diffuse = new(dr, dg, db, da);
            Specular = new(sr, sg, sb, sa);
            SpecularExponent = specularExponent;
            Ambient = new(ar, ag, ab, aa);
            MaterialAttributes = materialAttributes;
            UseAlpha = useAlpha;
            Culling = culling;
            SourceBlendMode = sourceBlendMode;
            DestinationBlendmode = destinationBlendmode;
            TextureIndex = textureIndex;
            TextureFiltering = textureFiltering;
            AnisotropicFiltering = anisotropicFiltering;
            MipmapDistanceAdjust = mipmapDistanceAdjust;
            ClampU = clampU;
            MirrorU = mirrorU;
            ClampV = clampV;
            MirrorV = mirrorV;
            ShadowStencil = shadowStencil;
            TexCoordID = texCoordID;
            TexGenType = texGenType;
            TexGenSrc = texGenSrc;
            MatrixID = matrixID;
        }

        internal BufferMaterial ToBufferMaterial()
        {
            return new()
            {
                Diffuse = Diffuse,
                Specular = Specular,
                SpecularExponent = SpecularExponent,
                Ambient = Ambient,
                MaterialAttributes = MaterialAttributes,
                UseAlpha = UseAlpha,
                BackfaceCulling = Culling,
                SourceBlendMode = SourceBlendMode,
                DestinationBlendmode = DestinationBlendmode,
                TextureIndex = TextureIndex,
                TextureFiltering = TextureFiltering,
                AnisotropicFiltering = AnisotropicFiltering,
                MipmapDistanceAdjust = MipmapDistanceAdjust,
                ClampU = ClampU,
                MirrorU = MirrorU,
                ClampV = ClampV,
                MirrorV = MirrorV,
                ShadowStencil = ShadowStencil,
                TexCoordID = TexCoordID,
                TexGenType = TexGenType,
                TexGenSrc = TexGenSrc,
                MatrixID = MatrixID,
            };
        }
    }

    public struct MeshStruct
    {
        public string Label { get; set; }
        public WeightedBufferVertex[] Vertices { get; set; }
        public BufferCorner[][] Corners { get; set; }
        public MaterialStruct[] Materials { get; set; }
        public int RootNodeIndex { get; set; }
        public bool HasVertexColors { get; set; }
        public bool ForceVertexColors { get; set; }

        public MeshStruct(
            string label,
            WeightedBufferVertex[] vertices,
            BufferCorner[][] corners,
            MaterialStruct[] materials,
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

        public WeightedBufferAttach ToWeightedBuffer(bool writeSpecular)
        {
            BufferMaterial[] materials = new BufferMaterial[Materials.Length];
            for(int j = 0; j < materials.Length; j++)
            {
                materials[j] = Materials[j].ToBufferMaterial();
            }

            WeightedBufferAttach wba = WeightedBufferAttach.Create(Vertices, Corners, materials, HasVertexColors);
            wba.Label = Label;
            wba.RootIndices.Add(RootNodeIndex);
            wba.ForceVertexColors = ForceVertexColors;
            wba.WriteSpecular = writeSpecular;

            return wba;
        }
    }

}
