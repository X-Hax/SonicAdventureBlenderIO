using Amicitia.IO.Binary;
using Amicitia.IO.Streams;
using SA3D.Archival;
using SA3D.Archival.PAK;
using SA3D.Archival.Textures;
using SA3D.Archival.Textures.GV;
using SA3D.Archival.Textures.PV;
using SA3D.Archival.Textures.PVX;
using SA3D.Common.IO;
using SA3D.Texturing;
using System;
using System.Diagnostics;
using System.Formats.Tar;
using System.Globalization;
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
				PAKEntry? infoEntry = pakArchive2.Entries.FirstOrDefault((PAKEntry x) => x.Name.EndsWith(".inf"));
				if(infoEntry != null)
				{
					int count = infoEntry.Data.Length / 60;
					PAKTextureInfo[] pakTextureInfo;
					using (MemoryStream stream = new(infoEntry.Data))
					{
						using BinaryObjectReader reader = new(stream, StreamOwnership.Retain, Endianness.Little);
						pakTextureInfo = reader.ReadObjectArray<PAKTextureInfo>(count);
					}

					foreach((Texture texture, PAKTextureInfo texInfo) in textures.Zip(pakTextureInfo))
					{
						PAKEntry entry = pakArchive2.Entries.FirstOrDefault(x => x.Name == texInfo.Name)
							?? pakArchive2.Entries.First(x => x.Name.StartsWith(texInfo.Name));

						texture.ImageFormat = DetectFormat(entry.Data);
						texture.PAKHasMipmaps = texInfo.Attributes.HasFlag(PAKTextureAttributes.Mipmapped);
						texture.PAKPunchthrough = texInfo.Type == GVTextureFormat.DXT1;
					}
				}
				else
				{
					foreach ((Texture texture, PAKEntry entry) in textures.Zip(pakArchive2.Entries))
					{
						texture.ImageFormat = DetectFormat(entry.Data);
					}
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
			if (data[0] == 0x44
				&& data[1] == 0x44
				&& data[2] == 0x53
				&& data[3] == 0x20)
			{

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
	}
}
