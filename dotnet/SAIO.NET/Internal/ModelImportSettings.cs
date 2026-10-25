using SA3D.Modeling.Convert;

namespace SAIO.NET.Internal
{
	internal struct ModelImportSettings
	{
		public bool UseQuaternions { get; set; }

		public WeightedMeshConverterParameters Parameters { get; set; }
	}
}
