using SA3D.Modeling.Convert.Weighted;
using System;

namespace SAIO.NET.External.Structs
{
	public unsafe struct CMesh : IConvertInternal<WeightedMesh>
	{
		public char* label;

		public int* weightNodeIndexMap;
		public int weightNodeIndexMapSize;

		public CVertex* vertices;
		public int verticesSize;

		public CCorner** triangleSets;
		public CMaterial* materials;
		public int* triangleSetSizes;
		public int triangleSetsSize;

		internal static CMesh FromInternal(WeightedMesh mesh)
		{
			CMesh result = new()
			{
				label = Allocate.AllocString(mesh.Label),
				
				weightNodeIndexMap = Allocate.AllocFromArray(mesh.WeightNodeIndexMap),
				weightNodeIndexMapSize = mesh.WeightNodeIndexMap?.Length ?? 0,
				
				vertices = Allocate.AllocFromArray(mesh.Vertices, CVertex.FromInternal),
				verticesSize = mesh.Vertices.Length,

				materials = Allocate.AllocFromArray(mesh.Materials, CMaterial.FromInternal),
				triangleSetsSize = mesh.TriangleSets.Length
			};

			Allocate.AllocFrom2DArray(mesh.TriangleSets, CCorner.FromInternal, out result.triangleSets, out result.triangleSetSizes);

			return result;
		}

		readonly internal WeightedMesh ToInternal()
		{
			int vertexWeightsSize = weightNodeIndexMapSize == 0 ? 0 : weightNodeIndexMapSize + 1;

			return new(
				Util.ToArray(vertices, verticesSize, v => v.ToInternal(vertexWeightsSize)) ?? throw new NullReferenceException("vertices is null"),
				Util.To2DArray<CCorner, WeightedCorner>(triangleSets, triangleSetsSize, triangleSetSizes) ?? throw new NullReferenceException("triangleSets is null"),
				Util.ToArray<CMaterial, WeightedMaterial>(materials, triangleSetsSize) ?? throw new NullReferenceException("materials is null"),
				Util.ToString(label)
			);
		}

		readonly WeightedMesh IConvertInternal<WeightedMesh>.ToInternal()
		{
			return ToInternal();
		}
	}
}
