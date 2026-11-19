using SAIO.NET.Internal;
using System;

namespace SAIO.NET.External.Structs
{
	public unsafe struct CTextureSet : IConvertInternal<TextureSet>
	{
		public CTexture* textures;
		public int texturesSize;

		public int archiveFormat;
		public bool compressedArchive;
		public int paletteHandling;

		internal static CTextureSet FromInternal(TextureSet textureSet)
		{
			return new()
			{
				textures = Allocate.AllocFromArray(textureSet.Textures, CTexture.FromInternal),
				texturesSize = textureSet.Textures.Length,
				archiveFormat = (int)textureSet.ArchiveFormat,
				compressedArchive = textureSet.Compress,
				paletteHandling = (int)textureSet.PaletteHandling
			};
		}

		readonly TextureSet IConvertInternal<TextureSet>.ToInternal()
		{
			return new(
				Util.ToArray<CTexture, Texture>(textures, texturesSize) ?? throw new NullReferenceException("Textures is null")
			)
			{
				ArchiveFormat = (TextureArchiveFormat)archiveFormat,
				Compress = compressedArchive,
				PaletteHandling = (TexturePaletteHandling)paletteHandling
			};
		}
	}
}
