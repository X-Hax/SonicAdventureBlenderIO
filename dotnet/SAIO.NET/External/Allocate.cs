using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;

namespace SAIO.NET.External
{
	public static unsafe class Allocate
	{
		private static readonly List<nint> _allocations = [];
		public static int WCharSize = sizeof(char);

		[UnmanagedCallersOnly(EntryPoint = "free_all")]
		public static void FreeAll()
		{
			foreach (nint pointer in _allocations)
			{
				Marshal.FreeHGlobal(pointer);
			}

			_allocations.Clear();
			ErrorHandler.ErrorMessage = null;
		}

		[UnmanagedCallersOnly(EntryPoint = "set_wchar_size")]
		public static void SetWCharSize(int size)
		{
			WCharSize = size;
		}


		public static T* Alloc<T>(int count = 1) where T : unmanaged
		{
			if (count == 0)
			{
				return null;
			}

			T* result = (T*)Marshal.AllocHGlobal(count * sizeof(T));
			_allocations.Add((nint)result);
			return result;
		}


		public static T* AllocFrom<T>(T data) where T : unmanaged
		{
			T* result = Alloc<T>();
			*result = data;
			return result;
		}

		public static O* AllocFrom<I, O>(I data, Func<I, O> convert) where O : unmanaged
		{
			O* result = Alloc<O>();
			*result = convert(data);
			return result;
		}

		public static O* AllocFrom<I, C, O>(I data, Func<I, C, O> convert, C context) where O : unmanaged
		{
			O* result = Alloc<O>();
			*result = convert(data, context);
			return result;
		}

		public static T* AllocFromArray<T>(IList<T>? values) where T : unmanaged
		{
			T* result = Alloc<T>(values?.Count ?? 0);

			if (result != null)
			{
				if (values is not T[] array)
				{
					array = [.. values!];
				}

				new Span<T>(array, 0, array.Length).CopyTo(new Span<T>(result, array.Length));
			}

			return result;
		}

		public static T** AllocPointersFromArray<T>(IList<T>? array) where T : unmanaged
		{
			if (array == null)
			{
				return null;
			}

			nint[] pointers = [.. array.Select(x => (nint)AllocFrom(x))];
			return (T**)AllocFromArray(pointers);
		}


		public static O* AllocFromArray<I, O>(IList<I>? values, Func<I, O> convert) where O : unmanaged
		{
			return AllocFromArray(values?.Select(convert).ToArray());
		}

		public static O** AllocPointersFromArray<I, O>(IList<I>? array, Func<I, O> convert) where O : unmanaged
		{
			if (array == null)
			{
				return null;
			}

			nint[] pointers = [.. array.Select(x => (nint)AllocFrom(x, convert))];
			return (O**)AllocFromArray(pointers);
		}


		public static O* AllocFromArray<I, C, O>(IList<I>? values, Func<I, C, O> convert, C context) where O : unmanaged
		{
			return AllocFromArray(values?.Select(x => convert(x, context)).ToArray());
		}

		public static O** AllocPointersFromArray<I, C, O>(IList<I>? array, Func<I, C, O> convert, C context) where O : unmanaged
		{
			if (array == null)
			{
				return null;
			}

			nint[] pointers = [.. array.Select(x => (nint)AllocFrom(x, convert, context))];
			return (O**)AllocFromArray(pointers);
		}

		public static void AllocFrom2DArray<T>(IList<IList<T>> values, out T** outValues) where T : unmanaged
		{
			if (values.Count == 0)
			{
				outValues = null;
				return;
			}

			T[] allValues = values.SelectMany(x => x).ToArray();
			T* outAllValues = AllocFromArray(allValues);

			outValues = (T**)Alloc<nint>(values.Count);

			T* currentValues = outAllValues;
			for (int i = 0; i < values.Count; i++)
			{
				outValues[i] = currentValues;
				currentValues += values[i].Count;
			}
		}

		public static void AllocFrom2DArray<T>(IList<IList<T>> values, out T** outValues, out int* outSizes) where T : unmanaged
		{
			AllocFrom2DArray(values, out outValues);

			outSizes = outValues != null
				? AllocFromArray(values.Select(x => x.Count).ToArray())
				: null;
		}


		public static char* AllocString(this string? value)
		{
			if (value == null)
			{
				return null;
			}

			char* result;

			if (WCharSize == sizeof(char))
			{
				result = (char*)Marshal.StringToHGlobalUni(value);
				_allocations.Add((nint)result);
			}
			else if (WCharSize == 4)
			{
				result = (char*)AllocFromArray(Encoding.UTF32.GetBytes(value + '\0'));
			}
			else
			{
				throw new NotSupportedException($"Unsupported character size: {WCharSize}");
			}

			return result;
		}

		public static char** AllocStringArray(IList<string>? values)
		{
			if (values == null)
			{
				return null;
			}

			char** result = (char**)Alloc<nint>(values.Count);

			for (int i = 0; i < values.Count; i++)
			{
				result[i] = values[i].AllocString();
			}

			return result;
		}
	}
}
