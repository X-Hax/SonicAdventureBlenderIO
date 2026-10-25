using SA3D.Modeling.Convert;
using SAIO.NET.Internal;

namespace SAIO.NET.External.Structs
{
	public struct CModelImportSettings : IConvertInternal<ModelImportSettings>
	{
		public bool useQuaternions;

		public CMeshConverterParameters meshConverterParameters;

		internal static CModelImportSettings FromInternal(ModelImportSettings settings)
		{
			return new()
			{
				useQuaternions = settings.UseQuaternions,
				meshConverterParameters = CMeshConverterParameters.FromInternal(settings.Parameters)
			};
		}

		ModelImportSettings IConvertInternal<ModelImportSettings>.ToInternal()
		{
			return new()
			{
				UseQuaternions = useQuaternions,
				Parameters = meshConverterParameters.ToInternal<CMeshConverterParameters, WeightedMeshConverterParameters>()
			};
		}
	}
}
