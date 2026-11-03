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
		public ushort attributes1;
		public ushort attributes2;
		public ushort attributes3;


		internal static CCorner FromInternal(WeightedCorner corner)
		{
			return new()
			{
				vertexIndex = corner.VertexIndex,
				diffuse = corner.Diffuse,
				specular = corner.Specular,
				texCoord = corner.TexCoord,
				attributes1 = corner.Attributes1, 
				attributes2 = corner.Attributes2, 
				attributes3 = corner.Attributes3
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
				Attributes1 = attributes1,
				Attributes2 = attributes2,
				Attributes3 = attributes3
			};
		}
	}
}
