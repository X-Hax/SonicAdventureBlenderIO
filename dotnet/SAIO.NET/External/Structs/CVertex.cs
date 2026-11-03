using SA3D.Modeling.Convert.Weighted;
using System.Numerics;

namespace SAIO.NET.External.Structs
{
	public unsafe struct CVertex
	{
		public Vector3 position;
		public Vector3 normal;
		public int userAttributes; // We use int here, since blender cannot handle uint values in attributes
		public float* weights; // no size, as that is indicated by the vertex container

		internal static CVertex FromInternal(WeightedVertex vertex)
		{
			return new()
			{
				position = vertex.Position,
				normal = vertex.Normal,
				userAttributes = unchecked((int)vertex.UserAttributes),
				weights = Allocate.AllocFromArray(vertex.Weights)
			};
		}

		internal readonly WeightedVertex ToInternal(int weightSize)
		{
			return new()
			{
				Position = position,
				Normal = normal,
				UserAttributes = unchecked((uint)userAttributes),
				Weights = weightSize == 0 ? null : Util.ToArray(weights, weightSize)
			};
		}
	}
}
