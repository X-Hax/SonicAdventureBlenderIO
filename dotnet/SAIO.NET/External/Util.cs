using System;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;

namespace SAIO.NET.External
{
	internal interface IConvertInternal<T>
	{
		public T ToInternal();
	}

	internal static unsafe class Util
	{
		public static O ToInternal<I, O>(this I input) where I : unmanaged, IConvertInternal<O>
		{
			return input.ToInternal();
		}


		public static T[]? ToArray<T>(T* values, int valuesSize) where T : unmanaged
		{
			if (values == null)
			{
				return null;
			}

			T[] result = new T[valuesSize];
			new Span<T>(values, valuesSize).CopyTo(new Span<T>(result, 0, valuesSize));
			return result;
		}

		public static O[]? ToArray<I, O>(I* values, int valuesSize) where I : unmanaged, IConvertInternal<O>
		{
			return ToArray(values, valuesSize)?.Select(x => x.ToInternal()).ToArray();
		}

		public static O[]? ToArray<I, O>(I* values, int valuesSize, Func<I, O> convert) where I : unmanaged
		{
			return ToArray(values, valuesSize)?.Select(x => convert(x)).ToArray();
		}

		public static O[]? PointersToArray<I, O>(I** values, int valuesSize) where I : unmanaged, IConvertInternal<O>
		{
			return ToArray((nint*)values, valuesSize)?.Select(x => ((I*)x)->ToInternal()).ToArray();
		}

		public static T[][]? To2DArray<T>(T** values, int valuesSize, int innerValuesSize) where T : unmanaged
		{
			if (values == null)
			{
				return null;
			}

			T[][] result = new T[valuesSize][];

			for (int i = 0; i < result.Length; i++)
			{
				result[i] = ToArray(values[i], innerValuesSize)!;
			}

			return result;
		}

		public static T[][]? To2DArray<T>(T** values, int valuesSize, int* innerValuesSizes) where T : unmanaged
		{
			if (values == null)
			{
				return null;
			}

			T[][] result = new T[valuesSize][];

			for (int i = 0; i < result.Length; i++)
			{
				result[i] = ToArray(values[i], innerValuesSizes[i])!;
			}

			return result;
		}

		public static O[][]? To2DArray<I, O>(I** values, int valuesSize, int innerValuesSize) where I : unmanaged, IConvertInternal<O>
		{
			if (values == null)
			{
				return null;
			}

			O[][] result = new O[valuesSize][];

			for (int i = 0; i < result.Length; i++)
			{
				result[i] = ToArray<I, O>(values[i], innerValuesSize)!;
			}

			return result;
		}

		public static O[][]? To2DArray<I, O>(I** values, int valuesSize, int* innerValuesSizes) where I : unmanaged, IConvertInternal<O>
		{
			if (values == null)
			{
				return null;
			}

			O[][] result = new O[valuesSize][];

			for (int i = 0; i < result.Length; i++)
			{
				result[i] = ToArray<I, O>(values[i], innerValuesSizes[i])!;
			}

			return result;
		}



		public static string? ToString(char* pointer)
		{
			if (Allocate.WCharSize == sizeof(char))
			{
				return Marshal.PtrToStringUni((nint)pointer);
			}
			else if (Allocate.WCharSize == 4)
			{
				if (pointer == null)
				{
					return null;
				}

				int* utf32 = (int*)pointer;
				int length = 0;

				while (utf32[length] != 0)
				{
					length++;
				}

				return Encoding.UTF32.GetString((byte*)pointer, length * 4);
			}
			else
			{
				throw new NotSupportedException($"Unsupported character size: {Allocate.WCharSize}");
			}
		}

		public static string[]? ToStringArray(char** values, int valuesSize)
		{
			if (values == null)
			{
				return null;
			}

			string[] result = new string[valuesSize];

			for (int i = 0; i < result.Length; i++)
			{
				result[i] = ToString(values[i])!;
			}

			return result;
		}

	}
}
