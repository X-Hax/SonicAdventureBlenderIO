using SA3D.Common.IO;
using SA3D.Modeling.Convert;
using SA3D.Modeling.File;
using SA3D.Modeling.File.MetaData.Blocks;
using SA3D.Modeling.Mesh;
using SA3D.Modeling.ObjectData.Enums;
using SA3D.Modeling.Structs;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using SA3DLevelModel = SA3D.Modeling.ObjectData.LevelModel;

namespace SAIO.NET.Internal
{
	internal class Level
	{
		public string Name { get; set; }
		public string Description { get; set; }
		public string Author { get; set; }
		public Format Format { get; set; }

		public RotationMode RotationMode { get; set; }

		public LevelModel[] Models { get; set; }
		public int VisualCount { get; set; }

		public MeshConversionInfo[] Meshes { get; set; }

		public LevelAttributes LevelAttributes { get; set; }
		public float DrawDistance { get; set; }
		public string? TextureFileName { get; set; }
		public uint TextureListAddress { get; set; }

		public Level(
			string label, 
			string description, 
			string author, 
			Format format, 
			RotationMode rotationMode,
			LevelModel[] models, 
			int collisionCount,
			MeshConversionInfo[] meshes, 
			LevelAttributes levelAttributes, 
			float drawDistance, 
			string? textureFileName, 
			uint textureListAddress)
		{
			Name = label;
			Description = description;
			Author = author;
			Format = format;
			RotationMode = rotationMode;
			Models = models;
			VisualCount = collisionCount;
			Meshes = meshes;
			LevelAttributes = levelAttributes;
			DrawDistance = drawDistance;
			TextureFileName = textureFileName;
			TextureListAddress = textureListAddress;
		}

		public static Level[] ReadFiles(string[] filepaths)
		{
			List<Level> result = [];

			foreach (string filepath in filepaths)
			{
				try
				{
					LevelFile levelFile = FileUtil.ReadFile<LevelFile>(filepath);
					string name = Path.GetFileNameWithoutExtension(filepath);

					string descripton = string.Empty;
					if (levelFile.MetaData.TryGetBlock(out DescriptionMetaDataBlock? descriptionBlock))
					{
						descripton = descriptionBlock!.Value;
					}

					string author = string.Empty;
					if (levelFile.MetaData.TryGetBlock(out AuthorMetaDataBlock? authorBlock))
					{
						author = authorBlock!.Value;
					}

					RotationMode rotationMode =
						levelFile.Level.Models.Any(x => x.Model.UseQuaternionRotation)
						? RotationMode.Quaternion
						: levelFile.Level.Models.Any(x => x.Model.RotateZYX)
						? RotationMode.EulerZYX
						: RotationMode.EulerXYZ;

					LevelModel[] models = new LevelModel[levelFile.Level.Models.Length];
					List<MeshData> meshData = [];
					int visualCount = 0;

					for(int i = 0; i < models.Length; i++)
					{
						SA3DLevelModel libModel = levelFile.Level.Models[i];

						if(libModel.Model.MeshData == null)
						{
							throw new NullReferenceException($"Level model [{i}] of level \"{name}\" has no mesh!");
						}

						if(libModel.Model.MeshData.MeshFormat is MeshFormat.Chunk or MeshFormat.Ginja)
						{
							visualCount++;
						}

						int meshIndex = meshData.IndexOf(libModel.Model.MeshData);
						if(meshIndex == -1)
						{
							meshIndex = meshData.Count;
							meshData.Add(libModel.Model.MeshData);
						}

						models[i] = new(libModel.Model, meshIndex, libModel.BlockBit, libModel.SurfaceAttributes);
					}

					// Note: Levelmodels have only one node with one mesh. A single meshdata instance should always result in
					// exactly one mesh info, or potentially zero, but in that case we'd have to question other things about the level
					MeshConversionInfo[] meshes = [.. meshData.Select(x => MeshConversionSet.ConvertToWeighted(new() { MeshData = x }).MeshInfo[0])];

					result.Add(new(
						name,
						descripton,
						author,
						levelFile.Level.Format,
						rotationMode,
						models,
						visualCount,
						meshes,
						levelFile.Level.Attributes,
						levelFile.Level.DrawDistance,
						levelFile.Level.TextureFileName,
						levelFile.Level.TextureListAddress
					));
				}
				catch (Exception exception)
				{
					throw new InvalidOperationException($"An exception occured while reading model file \"{filepath}\"!", exception);
				}
			}

			return [.. result];
		}
	}
}
