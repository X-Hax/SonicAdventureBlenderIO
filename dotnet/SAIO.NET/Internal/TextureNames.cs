using System;
using System.IO;
using System.Linq;

namespace SAIO.NET.Internal
{
	internal static class TextureNames
	{
		// AOT and INI de/serialization do not work, so we need to manually implement it here

		public static void WriteTextureNameListToFile(string filepath, string[] textureNames)
		{
			using StreamWriter writer = File.CreateText(filepath);

			string name = Path.GetFileNameWithoutExtension(filepath);
			writer.WriteLine($"Name={name}");
			writer.WriteLine($"TexnameArrayName={name}_names");
			writer.WriteLine($"NumTextures={textureNames.Length}");

			for (int i = 0; i < textureNames.Length; i++)
			{
				writer.WriteLine($"TextureNames[{i}]={textureNames[i]}");
			}

			writer.WriteLine();

			writer.Flush();
			writer.Close();
		}

		public static string[] ReadTextureNameListFromFrile(string filepath)
		{
			string[] lines = File.ReadAllLines(filepath);

			string? numTexturesLine = lines.FirstOrDefault(x => x.StartsWith("NumTextures="))
				?? throw new InvalidDataException("File is not a texture name list file!");

			if (!int.TryParse(numTexturesLine[12..], out int numTextures))
			{
				throw new InvalidDataException("File is not a valid texture name list file!");
			}

			string[] result = new string[numTextures];
			Array.Fill(result, string.Empty);

			foreach (string line in lines)
			{
				if (!line.StartsWith("TextureNames["))
				{
					continue;
				}

				int numberEnd = line.IndexOf(']');
				if (!int.TryParse(line[13..numberEnd], out int index))
				{
					throw new InvalidDataException("File is not a valid texture name list file!");
				}

				result[index] = line[(numberEnd + 2)..];
			}

			return result;
		}
	}
}
