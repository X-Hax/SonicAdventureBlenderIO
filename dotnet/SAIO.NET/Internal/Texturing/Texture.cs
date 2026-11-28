using BCnEncoder.Encoder;
using BCnEncoder.Shared;
using BCnEncoder.Shared.ImageFiles;
using SA3D.Archival.Textures.GV;
using SA3D.Archival.Textures.PV;
using SA3D.Archival.Textures.PVX;
using SA3D.Texturing;
using SA3D.Texturing.IO;
using SAIO.NET.External.Structs;
using System;
using System.IO;

namespace SAIO.NET.Internal.Texturing
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

		public bool PAKPunchthrough { get; set; }
		
		public TextureImageFormat ImageFormat { get; set; }
		public bool ImageHasMipMaps { get; set; }


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

		private static void FlipImage(byte[] pixels, int width, int height, int bpp)
		{
			// Images in blender start in the bottom left, instead of top left, so we gotta flip the image
			int halfHeight = height / 2;
			int rowWidth = width * bpp;
			for (int y = 0; y < halfHeight; y++)
			{
				int yStart = y * rowWidth;
				int yEnd = (height - (y + 1)) * rowWidth;

				for (int x = 0; x < rowWidth; x++)
				{
					int start = yStart + x;
					int end = yEnd + x;

					(pixels[start], pixels[end]) = (pixels[end], pixels[start]);
				}
			}
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

			FlipImage(pixels, texture.Width, texture.Height, 4);

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

		public static TextureImageFormat DetectImageFormat(ReadOnlySpan<byte> data, out bool hasMipmaps)
		{
			hasMipmaps = false;

			// Bitmap
			if (data[0] == 0x42
				&& data[1] == 0x4D)
			{
				return TextureImageFormat.BMP;
			}

			// JPG
			if (data[0] == 0xFF
				&& data[1] == 0xD8
				&& data[2] == 0xFF)
			{
				return TextureImageFormat.JPG;
			}

			// DDS
			if (data[0] == 0x44
				&& data[1] == 0x44
				&& data[2] == 0x53
				&& data[3] == 0x20)
			{

				hasMipmaps = data[28] > 0;

				if ((data[80] & 0x4) != 0 // fourCC flag check

					// fourCC value == DXT
					&& data[84] == 0x44
					&& data[85] == 0x58
					&& data[86] == 0x54)
				{
					switch (data[87])
					{
						case 0x31:
							return TextureImageFormat.DXT1;
						case 0x33:
							return TextureImageFormat.DXT3;
						case 0x35:
							return TextureImageFormat.DXT5;
					}
				}

				return TextureImageFormat.DDS;
			}

			return TextureImageFormat.PNG;
		}
	
		public ITexture ToSA3DTexture()
		{
			if(Type == TextureType.RGBA32)
			{
				byte[] pixels = (byte[])Pixels.Clone();
				FlipImage(pixels, Width, Height, 4);

				return new SA3D.Texturing.Texture(pixels, Width, Height, false)
				{
					Name = Name,
					GlobalIndex = unchecked((uint)GlobalIndex),
					OverrideHeight = OverrideHeight,
					OverrideWidth = OverrideWidth,
				};
			}
			else
			{
				byte[] indexPixels = new byte[Width * Height];
				for(int i = 0, o = 0; o < indexPixels.Length; o++, i += 4)
				{
					indexPixels[o] = Pixels[i];
				}
				FlipImage(indexPixels, Width, Height, 1);

				return new IndexTexture(indexPixels, Width, Height, Type == TextureType.Index4, false)
				{
					Name = Name,
					GlobalIndex = unchecked((uint)GlobalIndex),
					OverrideHeight = OverrideHeight,
					OverrideWidth = OverrideWidth,
				};
			}
		}

		public byte[] ConvertToImage()
		{
			ITexture texture = ToSA3DTexture();

			switch (ImageFormat)
			{
				case TextureImageFormat.DDS:
				case TextureImageFormat.DXT1:
				case TextureImageFormat.DXT3:
				case TextureImageFormat.DXT5:
					BcEncoder bcEncoder = new();

					bcEncoder.OutputOptions.GenerateMipMaps = ImageHasMipMaps;
					bcEncoder.OutputOptions.Format = ImageFormat switch
					{
						TextureImageFormat.DXT1 => CompressionFormat.Bc1,
						TextureImageFormat.DXT3 => CompressionFormat.Bc2,
						TextureImageFormat.DXT5 => CompressionFormat.Bc3,
						_ => CompressionFormat.Rgba
					};
					bcEncoder.OutputOptions.DdsPreferDxt10Header = false;
					bcEncoder.OutputOptions.DdsBc1WriteAlphaFlag = true;
					bcEncoder.OutputOptions.FileFormat = OutputFileFormat.Dds;

					DdsFile file = bcEncoder.EncodeToDds(texture.GetRGBA32Data(), texture.Width, texture.Height, PixelFormat.Rgba32);
					using (MemoryStream stream = new())
					{
						file.Write(stream);
						return stream.ToArray();
					}

				case TextureImageFormat.PNG:
					return TextureFileUtilities.WriteImageToBytes(texture, SA3D.Texturing.IO.ImageFormat.PNG);
				case TextureImageFormat.JPG:
					return TextureFileUtilities.WriteImageToBytes(texture, SA3D.Texturing.IO.ImageFormat.JPG);
				case TextureImageFormat.BMP:
					return TextureFileUtilities.WriteImageToBytes(texture, SA3D.Texturing.IO.ImageFormat.BMP);
				default:
					throw new ArgumentException($"Invalid image format \"{ImageFormat}\"");
			}
		}
	}
}
