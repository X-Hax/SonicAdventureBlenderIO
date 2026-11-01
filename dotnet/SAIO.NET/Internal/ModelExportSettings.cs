using SA3D.Modeling.Convert;

namespace SAIO.NET.Internal
{
	internal struct ModelExportSettings
	{
		public RotationMode RotationMode { get; set; }

		public WeightedMeshConverterParameters Parameters { get; set; }
	}
}
