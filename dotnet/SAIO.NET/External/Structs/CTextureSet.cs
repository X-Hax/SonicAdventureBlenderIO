using SA3D.Archival.Textures.GV;
using SA3D.Archival.Textures.PV;
using SA3D.Archival.Textures.PVX;
using SA3D.Texturing;
using SAIO.NET.Internal;

namespace SAIO.NET.External.Structs
{
	public unsafe struct CTextureSet
	{
		public CTexture* textures;
		public int texturesSize;

		public int archiveFormat;
		public bool compressedArchive;

		public static CTextureSet FromInternal(ITextureSet textureSet)
		{
			TextureArchiveFormat archiveFormat = textureSet switch
			{
				GVArchive => TextureArchiveFormat.GVM,
				PVArchive => TextureArchiveFormat.PVM,
				PVXArchive => TextureArchiveFormat.PVMX,
				_ => TextureArchiveFormat.PAK,
			};

			return new()
			{
				textures = Allocate.AllocFromArray(textureSet.Textures, CTexture.FromInternal),
				texturesSize = textureSet.Textures.Count,
				archiveFormat = (int)archiveFormat
			};
		}
	}
}
