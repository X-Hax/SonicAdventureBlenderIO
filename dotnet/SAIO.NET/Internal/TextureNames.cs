using SA3D.Modeling.TexName;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace SAIO.NET.Internal
{
	internal static class TextureNames
	{
		public static void WriteTextureNameListToFile(string filepath, string[] textureNames)
		{
			string filename = Path.GetFileNameWithoutExtension(filepath);
			TextureNameList list = new(filename, new(filename + "_names", [.. textureNames.Select(x => new TextureName(x, 0, 0))]));
			list.WriteAsIniToTextFile(filepath);
		}

		public static string[] ReadTextureNameListFromFrile(string filepath)
		{
			return [.. TextureNameList.ReadFromTextFile(filepath).TextureNames.Select(x => x.Name ?? string.Empty)];
		}
	}
}
