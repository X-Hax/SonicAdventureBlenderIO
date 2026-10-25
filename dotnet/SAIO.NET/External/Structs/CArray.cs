namespace SAIO.NET.External.Structs
{
	public unsafe struct CArray
	{
		public void* array;
		public int size;

		public CArray(void* array, int size)
		{
			this.array = array;
			this.size = size;
		}
	}
}
