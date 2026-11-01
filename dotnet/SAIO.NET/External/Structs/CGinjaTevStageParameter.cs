using SA3D.Modeling.Mesh.Ginja.Enums;
using SA3D.Modeling.Mesh.Ginja.Parameters;
using System;

namespace SAIO.NET.External.Structs
{
	public struct CGinjaTevStageParameter : IConvertInternal<GinjaTevStageParameter>
	{
		public byte tevStage;
		public byte texCoord;
		public byte texMap;
		public byte colorChannel;


		internal static CGinjaTevStageParameter FromInternal(GinjaTevStageParameter parameter)
		{
			return new()
			{
				tevStage = (byte)parameter.TevStage,
				texCoord = (byte)parameter.TexCoord,
				texMap = (byte)parameter.TexMap,
				colorChannel = (byte)parameter.ColorChannel,
			};
		}

		GinjaTevStageParameter IConvertInternal<GinjaTevStageParameter>.ToInternal()
		{
			return new()
			{
				TevStage = (GinjaTevStageID)tevStage,
				TexCoord = (GinjaTexCoordID)texCoord,
				TexMap = (GinjaTexMapID)texMap,
				ColorChannel = (GinjaColorChannelID)colorChannel,
			};
		}


		public readonly override int GetHashCode()
		{
			return HashCode.Combine(tevStage, texCoord, texMap, colorChannel);
		}
	}
}
