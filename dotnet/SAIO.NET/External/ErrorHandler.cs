using System;
using System.Runtime.InteropServices;

namespace SAIO.NET.External
{
	public static unsafe class ErrorHandler
	{
		public static char* ErrorMessage;

		public static void HandleError(Exception exception)
		{
			Console.WriteLine("A .NET error occured!");
			Console.WriteLine("Error message stack:");
			Exception? current = exception;
			while(current != null)
			{
				Console.WriteLine(current.GetType().Name);
				Console.WriteLine("  " + current.Message);
				Console.WriteLine();

				if(!string.IsNullOrWhiteSpace(current.StackTrace))
				{ 
					Console.WriteLine("Stack trace:");
					Console.WriteLine(current.StackTrace);
					Console.WriteLine();
				}

				current = current.InnerException;
			}

			ErrorMessage = exception.Message.AllocString();
		}

		[UnmanagedCallersOnly(EntryPoint = "error_get")]
		public static char* GetError()
		{
			return ErrorMessage;
		}
	}
}
