using SA3D.Modeling.Mesh.Ginja.Enums;
using SA3D.Modeling.Mesh.Ginja.Parameters;

namespace SAIO.NET.External.Structs
{
	public struct CGinjaTexGenParameter : IConvertInternal<GinjaTexGenParameter>
	{
		public byte texCoord;
		public byte texGenType;
		public byte texGenSource;
		public byte matrixID;

		public static CGinjaTexGenParameter FromInternal(GinjaTexGenParameter parameter)
		{
			return new()
			{
				texCoord = (byte)parameter.TexCoord,
				texGenType = (byte)parameter.TexGenType,
				texGenSource = (byte)parameter.TexGenSource,
				matrixID = (byte)parameter.MatrixID,
			};
		}

		GinjaTexGenParameter IConvertInternal<GinjaTexGenParameter>.ToInternal()
		{
			return new()
			{
				TexCoord = (GinjaTexCoordID)texCoord,
				TexGenType = (GinjaTexGenType)texGenType,
				TexGenSource = (GinjaTexGenSource)texGenSource,
				MatrixID = (GinjaTexGenMatrix)matrixID,
			};
		}
	}
}
