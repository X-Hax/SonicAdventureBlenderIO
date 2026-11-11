using SA3D.Archival.Textures;
using SA3D.Common.IO;
using SAIO.NET.External.Structs;
using SAIO.NET.Internal;
using System;
using System.ComponentModel;
using System.IO;
using System.Numerics;
using System.Runtime.InteropServices;

namespace SAIO.NET.External
{
	public static unsafe class ExternC
	{
		#region Matrix

		[UnmanagedCallersOnly(EntryPoint = "matrix_multiply")]
		public static Matrix4x4 MatrixMultiply(Matrix4x4 a, Matrix4x4 b)
		{
			try
			{
				return a * b;
			}
			catch (Exception exception)
			{
				ErrorHandler.HandleError(exception);
				return default;
			}
		}

		[UnmanagedCallersOnly(EntryPoint = "matrix_invert")]
		public static bool MatrixInvert(Matrix4x4* matrix)
		{
			try
			{
				bool result = Matrix4x4.Invert(*matrix, out Matrix4x4 invertedMatrx);
				*matrix = result ? invertedMatrx : Matrix4x4.Identity;
				return result;
			}
			catch (Exception exception)
			{
				ErrorHandler.HandleError(exception);
				return default;
			}
		}

		[UnmanagedCallersOnly(EntryPoint = "matrix_create_translation")]
		public static Matrix4x4 MatrixCreateTranslation(Vector3 position)
		{
			try
			{
				return Matrix4x4.CreateTranslation(position);
			}
			catch (Exception exception)
			{
				ErrorHandler.HandleError(exception);
				return default;
			}
		}

		[UnmanagedCallersOnly(EntryPoint = "matrix_create_rotation")]
		public static Matrix4x4 MatrixCreateRotation(Vector3 eulerRotation)
		{
			try
			{
				float sX = MathF.Sin(eulerRotation.X);
				float cX = MathF.Cos(eulerRotation.X);

				float sY = MathF.Sin(eulerRotation.Y);
				float cY = MathF.Cos(eulerRotation.Y);

				float sZ = MathF.Sin(eulerRotation.Z);
				float cZ = MathF.Cos(eulerRotation.Z);

				// equal to matX * matY * matZ
				return new()
				{
					M11 = cZ * cY,
					M12 = sZ * cY,
					M13 = -sY,

					M21 = (cZ * sY * sX) - (sZ * cX),
					M22 = (sZ * sY * sX) + (cZ * cX),
					M23 = cY * sX,

					M31 = (cZ * sY * cX) + (sZ * sX),
					M32 = (sZ * sY * cX) - (cZ * sX),
					M33 = cY * cX,

					M44 = 1
				};
			}
			catch (Exception exception)
			{
				ErrorHandler.HandleError(exception);
				return default;
			}
		}

		[UnmanagedCallersOnly(EntryPoint = "matrix_create_from_quaternion")]
		public static Matrix4x4 MatrixCreateFromQuaternion(Quaternion quaternion)
		{
			try
			{
				return Matrix4x4.CreateFromQuaternion(quaternion);
			}
			catch (Exception exception)
			{
				ErrorHandler.HandleError(exception);
				return default;
			}
		}

		[UnmanagedCallersOnly(EntryPoint = "matrix_create_scale")]
		public static Matrix4x4 MatrixCreateScale(Vector3 scale)
		{
			try
			{
				return Matrix4x4.CreateScale(scale);
			}
			catch (Exception exception)
			{
				ErrorHandler.HandleError(exception);
				return default;
			}
		}

		[UnmanagedCallersOnly(EntryPoint = "matrix_decompose")]
		public static void MatrixDecompose(Matrix4x4 matrix, Vector3* position, Quaternion* rotation, Vector3* scale)
		{
			try
			{
				Matrix4x4.Decompose(matrix, out *scale, out *rotation, out *position);
			}
			catch (Exception exception)
			{
				ErrorHandler.HandleError(exception);
				return;
			}
		}

		[UnmanagedCallersOnly(EntryPoint = "matrix_to_euler")]
		public static Vector3 MatrixToEuler(Matrix4x4 matrix)
		{
			try
			{
				const double threshold = 16 * 1.192092896e-07;
				double cy = double.Hypot(matrix.M11, matrix.M12);

				if (cy > threshold)
				{
					return new(
						MathF.Atan2(matrix.M23, matrix.M33),
						MathF.Atan2(-matrix.M13, (float)cy),
						MathF.Atan2(matrix.M12, matrix.M11)
					);

				}
				else
				{
					return new(
						MathF.Atan2(-matrix.M32, matrix.M22),
						MathF.Atan2(-matrix.M13, (float)cy),
						0f
					);
				}
			}
			catch (Exception exception)
			{
				ErrorHandler.HandleError(exception);
				return default;
			}
		}

		#endregion

		#region Quaternion

		[UnmanagedCallersOnly(EntryPoint = "quaternion_create_from_rotation_matrix")]
		public static Quaternion QuaternionCreateFromRotationMatrix(Matrix4x4 matrix)
		{
			try
			{
				return Quaternion.CreateFromRotationMatrix(matrix);
			}
			catch (Exception exception)
			{
				ErrorHandler.HandleError(exception);
				return default;
			}
		}

		#endregion

		#region Texture names

		[UnmanagedCallersOnly(EntryPoint = "texturename_read_file")]
		public static CArray TexturenameReadListFile(char* filepath)
		{
			try
			{
				string filepathString = Util.ToString(filepath) ?? throw new NullReferenceException("Filepath is null");

				string[] textureNames = TextureNames.ReadTextureNameListFromFrile(filepathString);

				return new(
					Allocate.AllocStringArray(textureNames),
					textureNames.Length
				);
			}
			catch (Exception exception)
			{
				ErrorHandler.HandleError(exception);
				return default;
			}
		}

		[UnmanagedCallersOnly(EntryPoint = "texturename_write_file")]
		public static void TexturenameWriteListFile(char* filepath, char** textureNames, int textureNamesSize)
		{
			try
			{
				string filepathString = Util.ToString(filepath) ?? throw new NullReferenceException("Filepath is null");
				string[] textureNamesArray = Util.ToStringArray(textureNames, textureNamesSize)!;

				TextureNames.WriteTextureNameListToFile(filepathString, textureNamesArray);
			}
			catch (Exception exception)
			{
				ErrorHandler.HandleError(exception);
			}
		}

		#endregion

		#region Textures

		[UnmanagedCallersOnly(EntryPoint = "texture_read_archive_file")]
		public static CTextureSet TextureReadArchiveFile(char* filepath)
		{
			try
			{
				string filepathString = Util.ToString(filepath) ?? throw new NullReferenceException("Filepath is null");
				FileIOInfo fileIOInfo = new(filepathString);

				if(!ITextureArchive.TryReadTextureArchiveFromFile(fileIOInfo, out ITextureArchive? archive))
				{
					throw new InvalidDataException("File is not a texture archive");
				}

				CTextureSet result = CTextureSet.FromInternal(archive);
				result.compressedArchive = Path.GetExtension(filepathString).ToLower() == ".prs";
				return result;
			}
			catch (Exception exception)
			{
				ErrorHandler.HandleError(exception);
				return default;
			}
		}

		#endregion

		#region Material

		[UnmanagedCallersOnly(EntryPoint = "material_get_hash")]
		public static int MaterialGetHashCode(CMaterial* material)
		{
			return material->GetHashCode();
		}

		#endregion

		#region Model

		[UnmanagedCallersOnly(EntryPoint = "model_read_files")]
		public static CArray ModelReadFiles(char** filepaths, int filepathsSize)
		{
			try
			{
				string[] filepathsArray = Util.ToStringArray(filepaths, filepathsSize)!;
				Model[] models = Model.ReadFiles(filepathsArray);
				CModel** result = Allocate.AllocPointersFromArray(models, CModel.FromInternal);

				return new(
					result,
					models.Length
				);
			}
			catch (Exception exception)
			{
				ErrorHandler.HandleError(exception);
				return default;
			}
		}

		#endregion
	}
}
