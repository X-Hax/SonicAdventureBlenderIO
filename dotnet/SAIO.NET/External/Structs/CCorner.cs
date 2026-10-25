using SA3D.Modeling.Convert.Weighted;
using System.Numerics;

namespace SAIO.NET.External.Structs
{
	public struct CCorner : IConvertInternal<WeightedCorner>
	{
		public ushort vertexIndex;
		public Vector4 diffuse;
		public Vector4 specular;
		public Vector2 texCoord;


		internal static CCorner FromInternal(WeightedCorner parameter)
		{
			return new()
			{
				vertexIndex = parameter.VertexIndex,
				diffuse = parameter.Diffuse,
				specular = parameter.Specular,
				texCoord = parameter.TexCoord,
			};
		}

		WeightedCorner IConvertInternal<WeightedCorner>.ToInternal()
		{
			return new()
			{
				VertexIndex = vertexIndex,
				Diffuse = diffuse,
				Specular = specular,
				TexCoord = texCoord,
			};
		}
	}
}
