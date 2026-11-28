using SA3D.Archival.Textures.GV;
using SA3D.Archival.Textures.PV;
using SA3D.Texturing;
using SAIO.NET.Internal.Texturing;
using System;
using Texture = SAIO.NET.Internal.Texturing.Texture;



namespace SAIO.NET.External.Structs
{
	public unsafe struct CTexture : IConvertInternal<Texture>
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

		public bool pakPunchthrough;

		public int imageFormat;
		public bool imageHasMipmaps;


		internal static CTexture FromInternal(Texture texture)
		{
			return new()
			{
				name = Allocate.AllocString(texture.Name),
				width = texture.Width,
				height = texture.Height,
				textureType = (int)texture.Type,
				pixels = Allocate.AllocFromArray(texture.Pixels),
				globalIndex = texture.GlobalIndex,
				dither = texture.Dither,
				gvFormat = (int)texture.GVFormat,
				gvHasMipmaps = texture.GVHasMipmaps,
				gvStorePalette = texture.GVStorePalette,
				gvPaletteFormat = (int)texture.GVPaletteFormat,
				pvDataFormat = (int)texture.PVDataFormat,
				pvPixelFormat = (int)texture.PVPixelFormat,
				overrideWidth = texture.OverrideWidth,
				overrideHeight = texture.OverrideHeight,
				pakPunchthrough = texture.PAKPunchthrough,
				imageFormat = (int)texture.ImageFormat,
				imageHasMipmaps = texture.ImageHasMipMaps,
			};
		}

		readonly Texture IConvertInternal<Texture>.ToInternal()
		{
			return new(
				Util.ToString(name) ?? throw new NullReferenceException("Name is null"),
				width,
				height,
				(TextureType)textureType,
				Util.ToArray(pixels, width * height * 4) ?? throw new NullReferenceException("Pixels is null"))
			{
				GlobalIndex = globalIndex,
				Dither = dither,
				GVFormat = (GVTextureFormat)gvFormat,
				GVHasMipmaps = gvHasMipmaps,
				GVStorePalette = gvStorePalette,
				GVPaletteFormat = (GVPaletteFormat)gvPaletteFormat,
				PVDataFormat = (PVTextureDataFormat)pvDataFormat,
				PVPixelFormat = (PVPixelFormat)pvPixelFormat,
				OverrideWidth = overrideWidth,
				OverrideHeight = overrideHeight,
				PAKPunchthrough = pakPunchthrough,
				ImageFormat = (TextureImageFormat)imageFormat,
				ImageHasMipMaps = imageHasMipmaps,
			};
		}
	}
}
