using SA3D.Modeling.Convert;
using SA3D.Modeling.ObjectData.Enums;
using SA3D.Modeling.Structs;
using SAIO.NET.Internal;
using System;
using System.Linq;

namespace SAIO.NET.External.Structs
{
	public unsafe struct CLevel : IConvertInternal<Level>
	{
		public char* name;
		public char* description;
		public char* author;
		public int format;

		public int rotationMode;

		public CLevelModel* models;
		public int modelsSize;
		public int visualCount;

		public CMeshConversionInfo* meshes;
		public int meshesSize;

		public int levelAttributes;
		public float drawDistance;
		public char* textureFileName;
		public int textureListAddress;

		internal static CLevel FromInternal(Level level)
		{
			CLevel result = new()
			{
				name = Allocate.AllocString(level.Name),
				description = Allocate.AllocString(level.Description),
				author = Allocate.AllocString(level.Author),
				format = (int)level.Format,

				models = Allocate.AllocFromArray(level.Models, CLevelModel.FromInternal),
				modelsSize = level.Models.Length,
				visualCount = level.VisualCount,

				meshes = Allocate.AllocFromArray(level.Meshes, CMeshConversionInfo.FromInternal),
				meshesSize = level.Meshes.Length,

				levelAttributes = unchecked((int)level.LevelAttributes),
				drawDistance = level.DrawDistance,
				textureFileName = Allocate.AllocString(level.TextureFileName),
				textureListAddress = unchecked((int)level.TextureListAddress)
			};

			return result;
		}

		readonly Level IConvertInternal<Level>.ToInternal()
		{
			return new(
				Util.ToString(name) ?? throw new NullReferenceException("name is null"),
				Util.ToString(description) ?? string.Empty,
				Util.ToString(author) ?? string.Empty,
				(Format)format,
				(RotationMode)rotationMode,
				CLevelModel.ArrayToInternal(models, modelsSize, (RotationMode)rotationMode),
				visualCount,
				Util.ToArray<CMeshConversionInfo, MeshConversionInfo>(meshes, meshesSize)
					?? throw new NullReferenceException("meshes is null"),
				unchecked((LevelAttributes)levelAttributes),
				drawDistance,
				Util.ToString(textureFileName),
				unchecked((uint)textureListAddress)
			);
		}
	}
}
