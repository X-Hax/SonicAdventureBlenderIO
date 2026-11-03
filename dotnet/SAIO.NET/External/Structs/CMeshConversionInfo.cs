using SA3D.Modeling.Convert;
using SA3D.Modeling.Mesh.Chunk;

namespace SAIO.NET.External.Structs
{
	public unsafe struct CMeshConversionInfo : IConvertInternal<MeshConversionInfo>
	{
		public CMesh mesh;

		public int attachedNodeIndex;

		public bool hasNormals;
		public bool hasVertexUserAttributes;
		public bool hasDiffuseColors;
		public bool hasSpecularColors;
		public bool volumeMesh;
		public byte chunkVertexType;
		public bool noBounds;

		internal static CMeshConversionInfo FromInternal(MeshConversionInfo info)
		{
			return new()
			{
				mesh = CMesh.FromInternal(info.Mesh),

				attachedNodeIndex = info.AttachedNodeIndex,

				hasNormals = info.HasNormals,
				hasVertexUserAttributes = info.HasVertexUserAttributes,
				hasDiffuseColors = info.HasDiffuseColors,
				hasSpecularColors = info.HasSpecularColors,
				volumeMesh = info.VolumeMesh,
				chunkVertexType = (byte)((byte)info.ChunkVertexType - 32),
				noBounds = info.NoBounds
			};
		}

		readonly MeshConversionInfo IConvertInternal<MeshConversionInfo>.ToInternal()
		{
			return new(mesh.ToInternal())
			{
				AttachedNodeIndex = attachedNodeIndex,
				HasNormals = hasNormals,
				HasVertexUserAttributes = hasVertexUserAttributes,
				HasDiffuseColors = hasDiffuseColors,
				HasSpecularColors = hasSpecularColors,
				VolumeMesh = volumeMesh,
				ChunkVertexType = (VertexChunkType)(chunkVertexType + 32),
				NoBounds = noBounds,
			};
		}
	}
}
