using SA3D.Modeling.ObjectData;

namespace SAIO.NET.Internal
{
	internal class LevelModel
	{
		public Node Node { get; set; }
		public int MeshIndex { get; set; }
		public uint BlockBit { get; set; }
		public uint SurfaceAttributes { get; set; }

		public LevelModel(Node node, int meshIndex, uint blockBit, uint surfaceAttributes)
		{
			Node = node;
			MeshIndex = meshIndex;
			BlockBit = blockBit;
			SurfaceAttributes = surfaceAttributes;
		}
	}
}
