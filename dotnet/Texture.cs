using SA3D.Texturing;
using System;
using Image = SA3D.Texturing.Texture;

namespace SAIO.NET
{
    public static class Texture
    {
        public static float[] GetData(Image texture)
        {
            const float factor = 1 / (float)byte.MaxValue;
            ReadOnlySpan<byte> pixels = texture.GetColorPixels();
            float[] result = new float[pixels.Length];

            int destIndex = 0;
            int pixRowSize = texture.Width * 4;
            for(int y = texture.Height - 1; y >= 0; y--)
            {
                ReadOnlySpan<byte> row = pixels[(y * pixRowSize)..];
                for(int x = 0; x < pixRowSize; x++)
                {
                    result[destIndex] = row[x] * factor;
                    destIndex++;
                }
            }

            return result;
        }

        public static Image Create(string name, int globalIndex, int width, int height, bool? index4, float[] colors)
        {
            ReadOnlySpan<float> source = colors;
            int destIndex = 0;
            int pixRowSize = width * 4;

            uint unsignedGlobalIndex = unchecked((uint)globalIndex);

            if(index4 == null)
            {
                byte[] pixelData = new byte[width * height * 4];

                for(int y = height - 1; y >= 0; y--)
                {
                    ReadOnlySpan<float> row = source[(y * pixRowSize)..];
                    for(int x = 0; x < pixRowSize; x++)
                    {
                        pixelData[destIndex] = (byte)(row[x] * 255);
                        destIndex++;
                    }
                }

                return new ColorTexture(width, height, pixelData, name, unsignedGlobalIndex);
            }
            else
            {
                byte[] pixelData = new byte[width * height];

                for(int y = height - 1; y >= 0; y--)
                {
                    ReadOnlySpan<float> row = source[(y * pixRowSize)..];
                    for(int x = 0; x < pixRowSize; x += 4)
                    {
                        byte r = (byte)(row[x] * 255);
                        byte g = (byte)(row[x + 1] * 255);
                        byte b = (byte)(row[x + 2] * 255);

                        pixelData[destIndex] = TextureUtilities.GetLuminance(r, g, b);
                        destIndex++;
                    }
                }

                return new IndexTexture(width, height, pixelData, name, unsignedGlobalIndex)
                {
                    IsIndex4 = index4.Value
                };
            }
        }
    
        public static int ToSigned(uint number)
        {
            return unchecked((int)number);
        }
    }
}
