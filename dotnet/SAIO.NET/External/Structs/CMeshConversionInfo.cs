using SA3D.Modeling.Convert;
using SA3D.Modeling.Mesh.Chunk;
using System;
using System.Linq;

namespace SAIO.NET.External.Structs
{
	public unsafe struct CMeshConversionInfo : IConvertInternal<MeshConversionInfo>
	{
		public CMesh mesh;

		public int* attachedNodeIndices;
		public int attachedNodeIndicesSize;

		public bool hasNormals;
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

				attachedNodeIndices = Allocate.AllocFromArray(info.AttachedNodeIndices.ToArray()),
				attachedNodeIndicesSize = info.AttachedNodeIndices.Count,

				hasNormals = info.HasNormals,
				hasDiffuseColors = info.HasDiffuseColors,
				hasSpecularColors = info.HasSpecularColors,
				volumeMesh = info.VolumeMesh,
				chunkVertexType = (byte)info.ChunkVertexType,
				noBounds = info.NoBounds
			};
		}

		readonly MeshConversionInfo IConvertInternal<MeshConversionInfo>.ToInternal()
		{
			return new(
				((IConvertInternal<SA3D.Modeling.Convert.Weighted.WeightedMesh>)mesh).ToInternal(),
				Util.ToArray(attachedNodeIndices, attachedNodeIndicesSize) ?? throw new NullReferenceException("attachedNodeIndices is null!"))
			{
				HasNormals = hasNormals,
				HasDiffuseColors = hasDiffuseColors,
				HasSpecularColors = hasSpecularColors,
				VolumeMesh = volumeMesh,
				ChunkVertexType = (VertexChunkType)chunkVertexType,
				NoBounds = noBounds,
			};
		}
	}
}
