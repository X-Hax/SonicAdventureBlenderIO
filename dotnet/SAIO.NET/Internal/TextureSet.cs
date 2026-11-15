using SA3D.Archival;
using SA3D.Archival.PAK;
using SA3D.Archival.Textures;
using SA3D.Archival.Textures.GV;
using SA3D.Archival.Textures.PV;
using SA3D.Archival.Textures.PVX;
using SA3D.Texturing;
using System;
using System.Diagnostics;
using System.IO;
using System.Linq;

namespace SAIO.NET.Internal
{
	internal class TextureSet
	{
		public Texture[] Textures { get; }
		public TextureArchiveFormat ArchiveFormat { get; set; }
		public bool Compress { get; set; }

		public TextureSet(Texture[] textures)
		{
			Textures = textures;
		}

		public static TextureSet ReadTextureArchive(string filepath)
		{
			if (!IArchive.TryReadArchiveFromFile(new(filepath), out IArchive? archive))
			{
				throw new InvalidDataException("File is not a texture archive");
			}

			ITextureSet textureSet;
			TextureArchiveFormat archiveFormat;

			if (archive is PAKArchive pakArchive)
			{
				archiveFormat = TextureArchiveFormat.PAK;
				textureSet = pakArchive.ToTextureSet();
			}
			else if (archive is ITextureArchive textureArchive)
			{
				archiveFormat = textureArchive switch
				{
					GVArchive => TextureArchiveFormat.GVM,
					PVArchive => TextureArchiveFormat.PVM,
					PVXArchive => TextureArchiveFormat.PVMX,
					_ => throw new UnreachableException()
				};

				textureSet = textureArchive;
			}
			else
			{
				throw new InvalidDataException("File is not a texture archive");
			}

			Texture[] textures = [.. textureSet.Textures.Select(Texture.FromITexture)];

			if (archive is PAKArchive pakArchive2)
			{
				foreach ((Texture texture, PAKEntry entry) in textures.Zip(pakArchive2.Entries))
				{
					texture.ImageFormat = DetectFormat(entry.Data);
				}
			}
			else if(archive is PVXArchive pvxArchive)
			{
				foreach ((Texture texture, PVXTexture pvx) in textures.Zip(pvxArchive.Entries))
				{
					texture.ImageFormat = DetectFormat(pvx.Data);
				}
			}

			return new(textures)
			{
				ArchiveFormat = archiveFormat,
				Compress = Path.GetExtension(filepath).Equals(".prs", StringComparison.InvariantCultureIgnoreCase)
			};
		}
	
		private static TextureImageFormat DetectFormat(ReadOnlySpan<byte> data)
		{
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
			if (// Signature check
				data[0] == 0x44
				&& data[1] == 0x44
				&& data[2] == 0x53
				&& data[3] == 0x20

				// fourCC flag check
				&& (data[84] & 0x4) != 0

				// fourCC value check)
				&& data[88] == 0x44
				&& data[89] == 0x58
				&& data[90] == 0x31
				&& data[91] == 0x30
				
				// format check
				&& data[129] == 0 
				&& data[130] == 0 
				&& data[131] == 0
				)
			{
				switch (data[128])
				{
					case 70: // BC1_TYPELESS
					case 71: // BC1_UNORM
					case 72: // BC1_UNORM_SRGB
						return TextureImageFormat.DDSBC1;
					case 73: // BC2_TYPELESS
					case 74: // BC2_UNORM
					case 75: // BC2_UNORM_SRGB
						return TextureImageFormat.DDSBC2;
					case 76: // BC3_TYPELESS
					case 77: // BC3_UNORM
					case 78: // BC3_UNORM_SRGB
						return TextureImageFormat.DDSBC3;
				}
			}

			return TextureImageFormat.PNG;
		}
	}
}
