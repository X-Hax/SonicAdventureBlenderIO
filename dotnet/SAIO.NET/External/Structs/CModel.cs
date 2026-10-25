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

				meshes = Allocate.AllocFromArray(model.Meshes.MeshInfo, CMeshConversionInfo.FromInternal),
				meshesSize = model.Meshes.MeshInfo.Count
			};

			result.nodes = CNode.ArrayFromInternal(model.RootNode, out result.nodesSize);

			return result;
		}

		internal Model ToInternal(bool useQuaternions)
		{
			return new(
				Util.ToString(name) ?? throw new NullReferenceException("name is null"),
				Util.ToString(description) ?? string.Empty,
				Util.ToString(author) ?? string.Empty,
				CNode.ArrayToInternal(nodes, nodesSize, useQuaternions),
				new() { MeshInfo = [.. 
					Util.ToArray<CMeshConversionInfo, MeshConversionInfo>(meshes, meshesSize) 
					?? throw new NullReferenceException("meshes is null")] }
			);
		}
	}
}
