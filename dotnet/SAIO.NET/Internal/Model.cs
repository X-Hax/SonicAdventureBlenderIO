using SA3D.Common.IO;
using SA3D.Modeling.Convert;
using SA3D.Modeling.File;
using SA3D.Modeling.File.MetaData.Blocks;
using SA3D.Modeling.ObjectData;
using System;
using System.Collections.Generic;
using System.IO;

namespace SAIO.NET.Internal
{
	internal class Model
	{
		public string Name { get; set; }
		public string Description { get; set; }
		public string Author { get; set; }

		public Node RootNode { get; set; }

		public MeshConversionSet Meshes { get; set; }

		public Model(string name, string description, string author, Node rootNode, MeshConversionSet meshes)
		{
			Name = name;
			Description = description;
			Author = author;
			RootNode = rootNode;
			Meshes = meshes;
		}

		public static Model[] ReadFiles(string[] filepaths, ModelImportSettings importSettings)
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

					MeshConversionSet meshes = MeshConversionSet.ConvertToWeighted(modelFile.Model);

					result.Add(new(
						Path.GetFileName(filepath),
						descripton,
						author,
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
