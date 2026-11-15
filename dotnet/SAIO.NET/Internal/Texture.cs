using SA3D.Archival.Textures.GV;
using SA3D.Archival.Textures.PV;
using SA3D.Archival.Textures.PVX;
using SA3D.Texturing;
using System;

namespace SAIO.NET.Internal
{
	internal class Texture
	{
		public string Name { get; }
		public int Width { get; }
		public int Height { get; }
		public TextureType Type { get; }
		public byte[] Pixels { get; }

		public int GlobalIndex { get; set; }
		public bool Dither { get; set; }

		public GVTextureFormat GVFormat { get; set; }
		public bool GVHasMipmaps { get; set; }
		public bool GVStorePalette { get; set; }
		public GVPaletteFormat GVPaletteFormat { get; set; }

		public PVTextureDataFormat PVDataFormat { get; set; }
		public PVPixelFormat PVPixelFormat { get; set; }

		public int OverrideWidth { get; set; }
		public int OverrideHeight { get; set; }

		public TextureImageFormat ImageFormat { get; set; }

		public Texture(string name, int width, int height, TextureType type, byte[] pixels)
		{
			if(pixels.Length != width * height * 4)
			{
				throw new ArgumentException($"Pixel length for texture {name} is {pixels.Length}, expected to be {width * height * 4} ({width} * {height} * 4)", nameof(pixels));
			}

			Name = name;
			Width = width;
			Height = height;
			Type = type;
			Pixels = pixels;
			ImageFormat = TextureImageFormat.PNG;
		}

		public static Texture FromITexture(ITexture texture)
		{
			byte[] pixels;

			if (texture.TextureType == TextureType.RGBA32)
			{
				pixels = texture.GetRGBA32Data().ToArray();
			}
			else if (texture is IIndexTexture indexTexture)
			{
				ReadOnlySpan<byte> paletteColors = ITexturePalette.GetDefaultPalette(indexTexture.IsIndex4).GetColorData();
				pixels = TextureUtilities.ApplyPaletteToIndexTexture(paletteColors, indexTexture.GetIndexPixelData(), indexTexture.IsIndex4);
			}
			else
			{
				throw new InvalidOperationException("Unsupported texture instance");
			}

			// Images in blender start in the bottom left, instead of top left, so we gotta flip the image
			int halfHeight = texture.Height / 2;
			int rowWidth = texture.Width * 4;
			for(int y = 0; y < halfHeight; y++)
			{
				int yStart = y * rowWidth;
				int yEnd = (texture.Height - (y + 1)) * rowWidth;

				for (int x = 0; x < rowWidth; x++)
				{
					int start = yStart + x;
					int end = yEnd + x;

					(pixels[start], pixels[end]) = (pixels[end], pixels[start]);
				}
			}

			Texture result = new(texture.Name, texture.Width, texture.Height, texture.TextureType, pixels)
			{
				GlobalIndex = unchecked((int)texture.GlobalIndex)
			};

			if (texture is GVTexture gvTexture)
			{
				result.GVFormat = gvTexture.TextureFormat;
				result.GVHasMipmaps = gvTexture.HasMipMaps;
				result.GVStorePalette = gvTexture.StorePalette;

				if (result.GVStorePalette)
				{
					result.GVPaletteFormat = ((GVPalette)gvTexture.Palette!).PaletteFormat;
				}
			}
			else if (texture is PVTexture pvTexture)
			{
				result.PVDataFormat = pvTexture.DataFormat;
				result.PVPixelFormat = pvTexture.PixelFormat;
			}
			else if (texture is PVXTexture pvxTexture)
			{
				result.OverrideWidth = pvxTexture.OverrideWidth;
				result.OverrideHeight = pvxTexture.OverrideHeight;
			}

			return result;
		}
	}
}
