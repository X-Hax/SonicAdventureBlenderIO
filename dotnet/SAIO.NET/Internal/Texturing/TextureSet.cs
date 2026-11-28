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
using SA3D.Texturing.IO;
using SAIO.NET.External.Structs;
using System;
using System.Diagnostics;
using System.Formats.Tar;
using System.Globalization;
using System.IO;
using System.Linq;

namespace SAIO.NET.Internal.Texturing
{
	internal class TextureSet
	{
		public Texture[] Textures { get; }
		public TextureArchiveFormat ArchiveFormat { get; set; }
		public bool Compress { get; set; }
		public TexturePaletteHandling PaletteHandling { get; set; }

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

						texture.ImageFormat = Texture.DetectImageFormat(entry.Data, out bool imageHasMipmaps);

						texture.ImageHasMipMaps =
							(imageHasMipmaps || texture.ImageFormat is TextureImageFormat.PNG or TextureImageFormat.JPG or TextureImageFormat.BMP)
							&& texInfo.Attributes.HasFlag(PAKTextureAttributes.Mipmapped);

						texture.PAKPunchthrough = texInfo.Type == GVTextureFormat.DXT1;
					}
				}
				else
				{
					foreach ((Texture texture, PAKEntry entry) in textures.Zip(pakArchive2.Entries))
					{
						texture.ImageFormat = Texture.DetectImageFormat(entry.Data, out bool imageHasMipmaps);
						texture.ImageHasMipMaps = imageHasMipmaps;
					}
				}
			}
			else if(archive is PVXArchive pvxArchive)
			{
				foreach ((Texture texture, PVXTexture pvx) in textures.Zip(pvxArchive.Entries))
				{
					texture.ImageFormat = Texture.DetectImageFormat(pvx.Data, out bool imageHasMipmaps);
					texture.ImageHasMipMaps = imageHasMipmaps;
				}
			}

			return new(textures)
			{
				ArchiveFormat = archiveFormat,
				Compress = Path.GetExtension(filepath).Equals(".prs", StringComparison.InvariantCultureIgnoreCase)
			};
		}
	
		public static TextureSet ImportTexturePack(string directory)
		{
			SA3D.Texturing.TextureSet texturePack = TextureFileUtilities.ImportTexturePack(directory);

			Texture[] textures = [.. texturePack.Textures.Select(Texture.FromITexture)];

			string indexPath = Path.Join(directory, "index.txt");
			string[] index = File.ReadAllLines(indexPath);

			foreach ((string item, Texture texture) in index.Zip(textures))
			{
				string[] values = item.Split(',');
				string filename = values[1];

				string texturePath = Path.Join(directory, filename);
				byte[] data = File.ReadAllBytes(texturePath);
				texture.ImageFormat = Texture.DetectImageFormat(data, out bool imageHasMipmaps);
				texture.ImageHasMipMaps = imageHasMipmaps;
			}

			return new(textures)
			{
				ArchiveFormat = TextureArchiveFormat.PVMX
			};
		}


		public void WriteTextureArchive(string filepath)
		{
			IArchive archive;

			switch (ArchiveFormat)
			{
				case TextureArchiveFormat.PAK:
					PAKEntry[] pakTextures = new PAKEntry[Textures.Length + 1];
					PAKTextureInfo[] pakTextureInfos = new PAKTextureInfo[Textures.Length];

					string filename = Path.GetFileNameWithoutExtension(filepath).ToLower();

					string pakDirectoryPath = Path.ChangeExtension(Path.GetFullPath(filepath), null).ToLower();
					if(Path.PathSeparator != '\\')
					{
						pakDirectoryPath = pakDirectoryPath.Replace(Path.PathSeparator, '\\');
					}

					int resourceStart = pakDirectoryPath.IndexOf("\\gd_pc\\");

					string pakPath = resourceStart != -1
						? "..\\..\\..\\sonic2\\resource" + pakDirectoryPath[resourceStart..] + '\\'
						: "..\\..\\..\\sonic2\\resource\\gd_pc\\prs\\" + filename + '\\';

					for (int i = 0; i < Textures.Length; i++)
					{
						Texture texture = Textures[i];

						string textureName = texture.Name.ToLower() + texture.ImageFormat switch
						{
							TextureImageFormat.DDS
							or TextureImageFormat.DXT1
							or TextureImageFormat.DXT3
							or TextureImageFormat.DXT5 => ".dds",
							TextureImageFormat.JPG => ".jpg",
							TextureImageFormat.BMP => ".bmp",
							_ => ".png",
						};

						pakTextures[i] = new(texture.ConvertToImage(), textureName, pakPath + textureName);

						pakTextureInfos[i] = new()
						{
							Name = textureName,
							GlobalIndex = unchecked((uint)texture.GlobalIndex),
							Type = texture.PAKPunchthrough ? GVTextureFormat.DXT1 : GVTextureFormat.RGB5A3,
							BitDepth = 0,
							PixelFormat = texture.PAKPunchthrough ? GVTextureFormat.DXT1 : GVTextureFormat.RGB5A3,
							Width = (uint)texture.Width,
							Height = (uint)texture.Height,
							DataSize = (uint)pakTextures[i].Data.Length,
							Attributes = texture.ImageHasMipMaps ? PAKTextureAttributes.Mipmapped : default
						};
					}

					using (MemoryStream pakTextureInfoStream = new())
					{
						BinaryObjectWriter writer = new(pakTextureInfoStream, StreamOwnership.Retain, Endianness.Little);
						writer.WriteObjectArray(pakTextureInfos);
						pakTextures[^1] = new(pakTextureInfoStream.ToArray(), filename + ".inf", pakPath + filename + ".inf");
					}

					archive = new PAKArchive(filename);
					((PAKArchive)archive).Entries.AddRange(pakTextures);

					break;
				case TextureArchiveFormat.GVM:
					GVArchive gvArchive = new();

					foreach (Texture texture in Textures)
					{
						GVTexture gvTexture = GVTexture.CreateFromTexture(
							texture.ToSA3DTexture(),
							texture.GVFormat,
							texture.GVHasMipmaps,
							texture.GVPaletteFormat,
							texture.Dither
						);

						gvArchive.Entries.Add(gvTexture);

						if(gvTexture.Palette != null)
						{
							if(texture.GVStorePalette)
							{
								gvTexture.StorePalette = texture.GVStorePalette;
							}
							else
							{
								switch (PaletteHandling)
								{
									case TexturePaletteHandling.Export:
										string paletteFilePath = Path.Join(Path.GetDirectoryName(filepath), gvTexture.Name + ".gvp");
										((GVPalette)gvTexture.Palette).WriteToFile(paletteFilePath);
										break;
									case TexturePaletteHandling.Embed:
										gvArchive.Palettes.Add((GVPalette)gvTexture.Palette);
										break;
								}
							}
						}
					}

					archive = gvArchive;
					break;
				case TextureArchiveFormat.PVM:
					PVArchive pvArchive = new();

					foreach (Texture texture in Textures)
					{
						PVTexture pvTexture = PVTexture.CreateFromTexture(
							texture.ToSA3DTexture(),
							texture.PVPixelFormat,
							texture.PVDataFormat,
							texture.Dither
						);

						pvArchive.Entries.Add(pvTexture);

						if (pvTexture.Palette != null)
						{
							switch (PaletteHandling)
							{
								case TexturePaletteHandling.Export:
									string paletteFilePath = Path.Join(Path.GetDirectoryName(filepath), pvTexture.Name + ".pvp");
									((PVPalette)pvTexture.Palette).WriteToFile(paletteFilePath);
									break;
								case TexturePaletteHandling.Embed:
									pvArchive.Palettes.Add((PVPalette)pvTexture.Palette);
									break;
							}
							
						}
					}

					archive = pvArchive;
					break;
				case TextureArchiveFormat.PVMX:
					PVXTexture[] pvxTextures = new PVXTexture[Textures.Length];
					for(int i = 0; i < Textures.Length; i++)
					{
						Texture texture = Textures[i];
						pvxTextures[i] = new()
						{
							Name = texture.Name,
							Data = texture.ConvertToImage(),
							GlobalIndex = unchecked((uint)texture.GlobalIndex),
							OverrideWidth = texture.OverrideWidth,
							OverrideHeight = texture.OverrideHeight,
						};
					}

					archive = new PVXArchive(pvxTextures);
					break;
				default:
					throw new InvalidOperationException("Invalid archive format");
			}

			byte[] data = archive.WriteToBytes(new(filepath));

			if(Compress)
			{
				data = PRS.Compress(data);
			}

			File.WriteAllBytes(filepath, data);
		}

		public void ExportTexturePack(string directory)
		{
			SA3D.Texturing.Texture[] textures = new SA3D.Texturing.Texture[Textures.Length];

			for(int i = 0; i < textures.Length; i++)
			{
				Texture texture = Textures[i];

				string name = texture.Name + texture.ImageFormat switch
				{
					TextureImageFormat.DDS 
					or TextureImageFormat.DXT1 
					or TextureImageFormat.DXT3 
					or TextureImageFormat.DXT5 => ".dds",
					TextureImageFormat.JPG => ".jpg",
					TextureImageFormat.BMP => ".bmp",
					_ => ".png",
				};

				textures[i] = new(texture.Pixels, texture.Width, texture.Height, false)
				{
					OverrideWidth = texture.OverrideWidth,
					OverrideHeight = texture.OverrideHeight,
					GlobalIndex = unchecked((uint)texture.GlobalIndex),
					Name = name
				};

				File.WriteAllBytes(
					Path.Join(directory, name),
					texture.ConvertToImage()
				);
			}

			SA3D.Texturing.TextureSet textureSet = new(textures);
			textureSet.WriteContentIndexToFile(Path.Join(directory, "index.txt"), string.Empty);
		}
	}
}
