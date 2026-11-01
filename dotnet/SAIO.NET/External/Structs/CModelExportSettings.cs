using SA3D.Modeling.Convert;
using SAIO.NET.Internal;

namespace SAIO.NET.External.Structs
{
	public struct CModelExportSettings : IConvertInternal<ModelExportSettings>
	{
		public int rotationMode;

		public CMeshConverterParameters meshConverterParameters;

		internal static CModelExportSettings FromInternal(ModelExportSettings settings)
		{
			return new()
			{
				rotationMode = (int)settings.RotationMode,
				meshConverterParameters = CMeshConverterParameters.FromInternal(settings.Parameters)
			};
		}

		ModelExportSettings IConvertInternal<ModelExportSettings>.ToInternal()
		{
			return new()
			{
				RotationMode = (RotationMode)rotationMode,
				Parameters = meshConverterParameters.ToInternal<CMeshConverterParameters, WeightedMeshConverterParameters>()
			};
		}
	}
}
