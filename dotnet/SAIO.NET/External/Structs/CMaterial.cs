using SA3D.Modeling.Convert.Weighted;
using SA3D.Modeling.Mesh;
using SA3D.Modeling.Mesh.Ginja.Parameters;
using System;
using System.Collections.Generic;
using System.Numerics;

namespace SAIO.NET.External.Structs
{
	public struct CMaterial : IConvertInternal<WeightedMaterial>
	{
		public Vector4 diffuse;
		public Vector3 specular;
		public float specularExponent;
		public Vector4 ambient;

		public bool useTexture;
		public uint textureIndex;

		public bool clampU;
		public bool clampV;
		public bool mirrorU;
		public bool mirrorV;
		public bool environmentMapping;
		public byte texcoordPrecisionLevel;

		public byte textureFilterMode;
		public bool anisotropicFiltering;
		public float mipmapDistanceMultiplier;

		public byte alphaMode;
		public byte sourceBlendMode;
		public byte destinationBlendMode;
		public bool doubleSided;

		public bool ignoreLighting;
		public bool ignoreAmbient;
		public bool ignoreSpecular;
		public bool flatShading;

		public CGinjaTevStageParameter ginjaTevStageParameter;
		public CGinjaTexGenParameter ginjaTexGenParameter;
		public bool ginjaUseVertexColorForDiffuse;
		public bool ginjaUseVertexColorForAmbient;
		public byte ginjaTextureSlot;


		public static CMaterial FromInternal(WeightedMaterial material)
		{
			return new()
			{
				diffuse = material.Diffuse,
				specular = material.Specular,
				specularExponent = material.SpecularExponent,
				ambient = material.Ambient,
				useTexture = material.UseTexture,
				textureIndex = material.TextureIndex,
				clampU = material.ClampU,
				clampV = material.ClampV,
				mirrorU = material.MirrorU,
				mirrorV = material.MirrorV,
				environmentMapping = material.EnvironmentMapping,
				texcoordPrecisionLevel = material.TexcoordPrecisionLevel,
				textureFilterMode = (byte)material.TextureFilterMode,
				anisotropicFiltering = material.AnisotropicFiltering,
				mipmapDistanceMultiplier = material.MipmapDistanceMultiplier,
				alphaMode = (byte)material.AlphaMode,
				sourceBlendMode = (byte)material.SourceBlendMode,
				destinationBlendMode = (byte)material.DestinationBlendMode,
				doubleSided = material.DoubleSided,
				ignoreLighting = material.IgnoreLighting,
				ignoreAmbient = material.IgnoreAmbient,
				ignoreSpecular = material.IgnoreSpecular,
				flatShading = material.FlatShading,
				ginjaTevStageParameter = CGinjaTevStageParameter.FromInternal(material.GinjaTevStageParameter),
				ginjaTexGenParameter = CGinjaTexGenParameter.FromInternal(material.GinjaTexGenParameter),
				ginjaUseVertexColorForDiffuse = material.GinjaUseVertexColorForDiffuse,
				ginjaUseVertexColorForAmbient = material.GinjaUseVertexColorForAmbient,
				ginjaTextureSlot = material.GinjaTextureSlot,
			};
		}

		readonly WeightedMaterial IConvertInternal<WeightedMaterial>.ToInternal()
		{
			return new()
			{
				Diffuse = diffuse,
				Specular = specular,
				SpecularExponent = specularExponent,
				Ambient = ambient,
				UseTexture = useTexture,
				TextureIndex = textureIndex,
				ClampU = clampU,
				ClampV = clampV,
				MirrorU = mirrorU,
				MirrorV = mirrorV,
				EnvironmentMapping = environmentMapping,
				TexcoordPrecisionLevel = texcoordPrecisionLevel,
				TextureFilterMode = (FilterMode)textureFilterMode,
				AnisotropicFiltering = anisotropicFiltering,
				MipmapDistanceMultiplier = mipmapDistanceMultiplier,
				AlphaMode = (AlphaMode)alphaMode,
				SourceBlendMode = (BlendMode)sourceBlendMode,
				DestinationBlendMode = (BlendMode)destinationBlendMode,
				DoubleSided = doubleSided,
				IgnoreLighting = ignoreLighting,
				IgnoreAmbient = ignoreAmbient,
				IgnoreSpecular = ignoreSpecular,
				FlatShading = flatShading,
				GinjaTevStageParameter = ginjaTevStageParameter.ToInternal<CGinjaTevStageParameter, GinjaTevStageParameter>(),
				GinjaTexGenParameter = ginjaTexGenParameter.ToInternal<CGinjaTexGenParameter, GinjaTexGenParameter>(),
				GinjaUseVertexColorForDiffuse = ginjaUseVertexColorForDiffuse,
				GinjaUseVertexColorForAmbient = ginjaUseVertexColorForAmbient,
				GinjaTextureSlot = ginjaTextureSlot,
			};
		}


		public readonly override int GetHashCode()
		{
			HashCode hash = new();
			hash.Add(diffuse);
			hash.Add(specular);
			hash.Add(specularExponent);
			hash.Add(ambient);
			hash.Add(useTexture);
			hash.Add(textureIndex);
			hash.Add(clampU);
			hash.Add(clampV);
			hash.Add(mirrorU);
			hash.Add(mirrorV);
			hash.Add(environmentMapping);
			hash.Add(texcoordPrecisionLevel);
			hash.Add(textureFilterMode);
			hash.Add(anisotropicFiltering);
			hash.Add(mipmapDistanceMultiplier);
			hash.Add(alphaMode);
			hash.Add(sourceBlendMode);
			hash.Add(destinationBlendMode);
			hash.Add(doubleSided);
			hash.Add(ignoreLighting);
			hash.Add(ignoreAmbient);
			hash.Add(ignoreSpecular);
			hash.Add(flatShading);
			hash.Add(ginjaTevStageParameter);
			hash.Add(ginjaTexGenParameter);
			hash.Add(ginjaUseVertexColorForDiffuse);
			hash.Add(ginjaUseVertexColorForAmbient);
			hash.Add(ginjaTextureSlot);
			return hash.ToHashCode();
		}
	}
}
