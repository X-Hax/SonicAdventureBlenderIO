using SA3D.Modeling.Convert;
using SAIO.NET.Internal;
using System;

namespace SAIO.NET.External.Structs
{
	public unsafe struct CModel
	{
		public char* name;
		public char* description;
		public char* author;
		public bool chaoChunk;

		public int rotationMode;

		public CNode* nodes;
		public int nodesSize;

		public CMeshConversionInfo* meshes;
		public int meshesSize;



		internal static CModel FromInternal(Model model)
		{
			CModel result = new()
			{
				name = Allocate.AllocString(model.Name),
				description = Allocate.AllocString(model.Description),
				author = Allocate.AllocString(model.Author),
				chaoChunk = model.ChaoChunk,

				meshes = Allocate.AllocFromArray(model.Meshes.MeshInfo, CMeshConversionInfo.FromInternal),
				meshesSize = model.Meshes.MeshInfo.Count
			};

			result.nodes = CNode.ArrayFromInternal(model.RootNode, out result.nodesSize);

			return result;
		}

		internal Model ToInternal()
		{
			return new(
				Util.ToString(name) ?? throw new NullReferenceException("name is null"),
				Util.ToString(description) ?? string.Empty,
				Util.ToString(author) ?? string.Empty,
				chaoChunk,
				(RotationMode)rotationMode,
				CNode.ArrayToInternal(nodes, nodesSize, (RotationMode)rotationMode),
				new() { MeshInfo = [.. 
					Util.ToArray<CMeshConversionInfo, MeshConversionInfo>(meshes, meshesSize) 
					?? throw new NullReferenceException("meshes is null")] }
			);
		}
	}
}
