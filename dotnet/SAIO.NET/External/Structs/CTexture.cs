using SA3D.Archival.Textures.GV;
using SA3D.Archival.Textures.PV;
using SA3D.Archival.Textures.PVX;
using SA3D.Texturing;
using System;

namespace SAIO.NET.External.Structs
{
	public unsafe struct CTexture
	{
		public char* name;
		public int width;
		public int height;
		public int textureType;
		public byte* pixels;

		public int globalIndex;
		public bool dither;

		public int gvFormat;
		public bool gvHasMipmaps;
		public bool gvStorePalette;
		public int gvPaletteFormat;

		public int pvDataFormat;
		public int pvPixelFormat;

		public int overrideWidth;
		public int overrideHeight;

		public int imageFormat;


		public static CTexture FromInternal(ITexture texture)
		{
			CTexture result = new()
			{
				name = Allocate.AllocString(texture.Name),
				width = texture.Width,
				height = texture.Height,
				textureType = (int)texture.TextureType,
				pixels = Allocate.Alloc<byte>(texture.Width * texture.Height * 4),
				globalIndex = unchecked((int)texture.GlobalIndex)
			};

			ReadOnlySpan<byte> pixelData;

			if (texture.TextureType == TextureType.RGBA32)
			{
				pixelData = texture.GetRGBA32Data();
			}
			else if(texture is IIndexTexture indexTexture)
			{
				ReadOnlySpan<byte> paletteColors = ITexturePalette.GetDefaultPalette(indexTexture.IsIndex4).GetColorData();
				pixelData = TextureUtilities.ApplyPaletteToIndexTexture(paletteColors, indexTexture.GetIndexPixelData(), indexTexture.IsIndex4);
			}
			else
			{
				throw new InvalidOperationException("Unsupported texture instance");
			}

			pixelData.CopyTo(new Span<byte>(result.pixels, pixelData.Length));

			if (texture is GVTexture gvTexture)
			{
				result.gvFormat = (int)gvTexture.TextureFormat;
				result.gvHasMipmaps = gvTexture.HasMipMaps;
				result.gvStorePalette = gvTexture.StorePalette;

				if(result.gvStorePalette)
				{
					result.gvPaletteFormat = (int)((GVPalette)gvTexture.Palette!).PaletteFormat;
				}
			}
			else if(texture is PVTexture pvTexture)
			{
				result.pvDataFormat = (int)pvTexture.DataFormat;
				result.pvPixelFormat = (int)pvTexture.PixelFormat;
			}
			else if(texture is PVXTexture pvxTexture)
			{
				result.overrideWidth = pvxTexture.OverrideWidth;
				result.overrideHeight = pvxTexture.OverrideHeight;
			}

			return result;
		}
	}
}
