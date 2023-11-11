using SA3D.Texturing;

namespace SA3D.Modeling.Blender
{
    public static class Texture
    {
        public static float[] GetData(Texturing.Texture texture)
        {
            const float factor = 1 / (float)byte.MaxValue;
            var pixels = texture.GetColorPixels();
            float[] result = new float[pixels.Length];

            int destIndex = 0;
            int pixRowSize = texture.Width * 4;
            for (int y = texture.Height - 1; y >= 0; y--)
            {
                ReadOnlySpan<byte> row = pixels.Slice(y * pixRowSize);
                for (int x = 0; x < pixRowSize; x++)
                {
                    result[destIndex] = row[x] * factor;
                    destIndex++;
                }
            }
            return result;
        }

        public static Texturing.Texture Create(string name, uint globalIndex, int width, int height, bool? index4, float[] colors)
        {
            ReadOnlySpan<float> source = colors;
            int destIndex = 0;
            int pixRowSize = width * 4;

            if (index4 == null)
            {
                byte[] pixelData = new byte[width * height * 4];

                for (int y = height - 1; y >= 0; y--)
                {
                    ReadOnlySpan<float> row = source.Slice(y * pixRowSize);
                    for (int x = 0; x < pixRowSize; x++)
                    {
                        pixelData[destIndex] = (byte)(row[x] * 255);
                        destIndex++;
                    }
                }

                return new Texturing.Texture(name, globalIndex, width, height, pixelData);
            }
            else
            {
                byte[] pixelData = new byte[width * height];

                for (int y = height - 1; y >= 0; y--)
                {
                    ReadOnlySpan<float> row = source.Slice(y * pixRowSize);
                    for (int x = 0; x < pixRowSize; x += 4)
                    {
                        byte r = (byte)(row[x] * 255);
                        byte g = (byte)(row[x + 1] * 255);
                        byte b = (byte)(row[x + 2] * 255);

                        pixelData[destIndex] = TextureUtils.GetLuminance(r, g, b);
                        destIndex++;
                    }
                }

                return new IndexTexture(name, globalIndex, width, height, pixelData, index4.Value);
            }
        }
    }
}
