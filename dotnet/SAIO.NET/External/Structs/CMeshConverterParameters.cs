using SA3D.Modeling.Convert;

namespace SAIO.NET.External.Structs
{
	public struct CMeshConverterParameters : IConvertInternal<WeightedMeshConverterParameters>
	{
		public bool splitWeighted;
		public bool useMetaWeights;
		public bool highPrecisionWeights;
		public bool mergeVertices;
		public float vertexMergeDistance;


		internal static CMeshConverterParameters FromInternal(WeightedMeshConverterParameters parameters)
		{
			return new()
			{
				splitWeighted = parameters.SplitWeighted,
				useMetaWeights = parameters.UseMetaWeights,
				highPrecisionWeights = parameters.HighPrecisionWeights,
				mergeVertices = parameters.MergeVertices,
				vertexMergeDistance = parameters.VertexMergeDistance,
			};
		}

		readonly WeightedMeshConverterParameters IConvertInternal<WeightedMeshConverterParameters>.ToInternal()
		{
			return new()
			{
				SplitWeighted = splitWeighted,
				UseMetaWeights = useMetaWeights,
				HighPrecisionWeights = highPrecisionWeights,
				MergeVertices = mergeVertices,
				VertexMergeDistance = vertexMergeDistance,
			};
		}
	}
}
