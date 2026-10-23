using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

namespace SAIO.NET.External
{
	public static unsafe class ErrorHandler
	{
		public static char* ErrorMessage;

		public static void HandleError(Exception exception)
		{
			Console.WriteLine("A .NET error occured!");
			Console.WriteLine("Error message:");
			Console.WriteLine("\t" + exception.Message);
			Console.WriteLine("Stack trace:");
			Console.WriteLine(exception.StackTrace);
			Console.WriteLine();

			ErrorMessage = exception.Message.AllocString();
		}

		[UnmanagedCallersOnly(EntryPoint = "error_get")]
		public static char* GetError()
		{
			return ErrorMessage;
		}
	}
}
