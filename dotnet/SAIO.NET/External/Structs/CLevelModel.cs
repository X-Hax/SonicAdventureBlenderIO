using SAIO.NET.Internal;

namespace SAIO.NET.External.Structs
{
	public struct CLevelModel
	{
		public CNode node;
		public int meshIndex;
		public int blockbit;
		public int surfaceAttributes;

		internal static CLevelModel FromInternal(LevelModel model)
		{
			return new()
			{
				node = CNode.FromInternal(model.Node, null),
				meshIndex = model.MeshIndex,
				blockbit = unchecked((int)model.BlockBit),
				surfaceAttributes = unchecked((int)model.SurfaceAttributes)
			};
		}

		internal readonly LevelModel ToInternal(RotationMode rotationMode)
		{
			return new(
				node.ToInternal(new(null, rotationMode)),
				meshIndex,
				unchecked((uint)blockbit),
				unchecked((uint)surfaceAttributes)
			);
		}

		internal static unsafe LevelModel[] ArrayToInternal(CLevelModel* models, int modelsSize, RotationMode rotationMode)
		{
			LevelModel[] resultModels = new LevelModel[modelsSize];

			for (int i = 0; i < modelsSize; i++)
			{
				resultModels[i] = models[i].ToInternal(rotationMode);
			}

			return resultModels;
		}
	}
}
