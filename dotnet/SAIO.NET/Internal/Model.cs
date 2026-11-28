using SA3D.Common.IO;
using SA3D.Modeling.Convert;
using SA3D.Modeling.File;
using SA3D.Modeling.File.MetaData;
using SA3D.Modeling.File.MetaData.Blocks;
using SA3D.Modeling.ObjectData;
using SA3D.Modeling.Structs;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace SAIO.NET.Internal
{
	internal class Model
	{
		public string Name { get; set; }
		public string Description { get; set; }
		public string Author { get; set; }
		public Format Format { get; set; }
		public bool ChaoChunk { get; set; }

		public RotationMode RotationMode { get; set; }

		public Node RootNode { get; set; }

		public MeshConversionSet Meshes { get; set; }

		public Model(string name, string description, string author, Format format, bool chaoChunk, RotationMode rotationMode, Node rootNode, MeshConversionSet meshes)
		{
			Name = name;
			Description = description;
			Author = author;
			Format = format;
			ChaoChunk = chaoChunk;
			RotationMode = rotationMode;
			RootNode = rootNode;
			Meshes = meshes;
		}

		public static Model[] ReadFiles(string[] filepaths)
		{
			List<Model> result = [];

			foreach (string filepath in filepaths)
			{
				try
				{
					ModelFile modelFile = FileUtil.ReadFile<ModelFile>(filepath);

					string descripton = string.Empty;
					if (modelFile.MetaData.TryGetBlock(out DescriptionMetaDataBlock? descriptionBlock))
					{
						descripton = descriptionBlock!.Value;
					}

					string author = string.Empty;
					if(modelFile.MetaData.TryGetBlock(out AuthorMetaDataBlock? authorBlock))
					{
						author = authorBlock!.Value;
					}

					bool chaoChunk = modelFile.MetaData.Blocks.Any(x => x is FlagMetaDataBlock flag && flag.Value == MetaDataFlags.ChaoChunk);

					RotationMode rotationMode =
						modelFile.Model.GetTreeNodeEnumerable().Any(x => x.UseQuaternionRotation)
						? RotationMode.Quaternion
						: modelFile.Model.GetTreeNodeEnumerable().Any(x => x.RotateZYX)
						? RotationMode.EulerZYX
						: RotationMode.EulerXYZ;

					MeshConversionSet meshes = MeshConversionSet.ConvertToWeighted(modelFile.Model);

					result.Add(new(
						Path.GetFileNameWithoutExtension(filepath),
						descripton,
						author,
						modelFile.Format,
						chaoChunk,
						rotationMode,
						modelFile.Model,
						meshes
					));
				}
				catch(Exception exception)
				{
					throw new InvalidOperationException($"An exception occured while reading model file \"{filepath}\"!", exception);
				}
			}

			return [.. result];
		}
	}
}
