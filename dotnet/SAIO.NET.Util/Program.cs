using CaseConverter;
using SAIO.NET.External;
using System.Numerics;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;

namespace SAIO.NET.Util
{
	internal class Program
	{
		private static readonly Dictionary<string, (string type, string hint)> _pythonTypeLookup = new()
        {
            { typeof(char*).FullName!, ("ctypes.c_wchar_p", "str") },
            { typeof(void*).FullName!, ("ctypes.c_void_p", "ctypes.c_void_p") },
            { typeof(nint).FullName!, ("ctypes.c_size_t", "ctypes.c_void_p") },
            { typeof(byte).FullName!, ("ctypes.c_ubyte", "int") },
            { typeof(short).FullName!, ("ctypes.c_short", "int") },
            { typeof(ushort).FullName!, ("ctypes.c_ushort", "int") },
            { typeof(int).FullName!, ("ctypes.c_int", "int") },
            { typeof(uint).FullName!, ("ctypes.c_uint", "int") },
            { typeof(long).FullName!, ("ctypes.c_longlong", "int") },
            { typeof(ulong).FullName!, ("ctypes.c_ulonglong", "int") },
            { typeof(float).FullName!, ("ctypes.c_float", "float") },
            { typeof(bool).FullName!, ("ctypes.c_bool", "bool") },

            { typeof(Vector2).FullName!, ("nettypes.CVector2", "nettypes.CVector2") },
            { typeof(Vector3).FullName!, ("nettypes.CVector3", "nettypes.CVector3") },
            { typeof(Vector4).FullName!, ("nettypes.CVector4", "nettypes.CVector4") },
            { typeof(Quaternion).FullName!, ("nettypes.CQuaternion", "nettypes.CQuaternion") },
            { typeof(Matrix4x4).FullName!, ("nettypes.CMatrix", "nettypes.CMatrix") },
        };

        private static readonly Type[] _saioStructTypes = [..
            Assembly.GetAssembly(typeof(External.ExternC))!
            .GetTypes()
            .Where(x => x.IsValueType && x.Namespace == "SAIO.NET.External.Structs")
        ];

        private static readonly HashSet<string> _saioStructTypeNames = [.. _saioStructTypes.Select(x => x.FullName!)!];

        static void Main(string[] args)
        {
            string currentDirectory = Directory.GetCurrentDirectory();

            string dotnetDirectory = currentDirectory;
            while (Path.GetFileName(dotnetDirectory) != "dotnet")
            {
                dotnetDirectory = Path.GetDirectoryName(dotnetDirectory)!;
            }

            string repoDirectory = Path.GetDirectoryName(dotnetDirectory)!;
            string externalDirectory = Path.Join(repoDirectory, "blender", "source", "external");

            GeneratePythonStructs(externalDirectory);
            GenerateDLLFunction(externalDirectory);
        }

        private static string TypeToFileName(string typeName)
        {
            return typeName[1..].ToSnakeCase();
        }

        private static bool GetPythonType(Type type, string saioStructPrefix, out string typeName, out string pythonType, out string pythonHint)
        {
            pythonType = string.Empty;
            pythonHint = string.Empty;
            typeName = type.FullName!;

            int pointerLevel = 0;
            while (true)
            {
                if (_saioStructTypeNames.Contains(typeName))
                {
                    string saioStructName = saioStructPrefix + type.Name[..^pointerLevel];
                    pythonType = saioStructName;
                    pythonHint = saioStructName;
                    break;
                }

                if (_pythonTypeLookup.TryGetValue(typeName, out (string type, string hint) pyType))
                {
                    pythonType = pyType.type;
                    pythonHint = pyType.hint;
                    break;
                }

                if (typeName.EndsWith('*'))
                {
                    pointerLevel++;
                    typeName = typeName[..^1];
                }
                else
                {
                    break;
                }
            }

            if (string.IsNullOrEmpty(pythonType))
            {
                return false;
            }

            for (int i = 0; i < pointerLevel; i++)
            {
                pythonType = $"ctypes.POINTER({pythonType})";

                if (i == 0)
                {
                    pythonHint = $"TPointer['{pythonHint}']";
                }
                else
                {
                    pythonHint = $"TPointer[{pythonHint}]";
                }
            }

            return true;
        }

        public static void GeneratePythonStructs(string externalDirectory)
        {
            string outputDirectory = Path.Join(externalDirectory, "structs");

            if(!Directory.Exists(outputDirectory))
            {
                Directory.CreateDirectory(outputDirectory);
            }

            StringBuilder initBuilder = new();

            foreach (Type type in _saioStructTypes)
            {
                StringBuilder builder = new();
                builder.AppendLine("# !!! GENERATED USING SAIO.NET.Utils !!!");
                builder.AppendLine("# Please do not touch manually!");

                builder.AppendLine("import ctypes");
                builder.AppendLine("from .. import nettypes");
                builder.AppendLine("from ..typing import TPointer");

                HashSet<string> usedSAIOTypes = [];
                List<(string name, string type, string hint)> fields = [];

                foreach (FieldInfo field in type.GetFields())
                {
                    if(!GetPythonType(field.FieldType, string.Empty, out string typeName, out string pythonType, out string pythonHint))
                    {
                        throw new InvalidOperationException($"Could not determine python field type for {type.Name}.{field.Name}: {field.FieldType.FullName}");
                    }

                    if(_saioStructTypeNames.Contains(typeName))
                    {
                        usedSAIOTypes.Add(typeName);
                    }

                    fields.Add((field.Name.ToSnakeCase(), pythonType, pythonHint));
                }

                foreach (string saioTypeName in usedSAIOTypes)
                {
                    if(saioTypeName == type.FullName)
                    {
                        continue;
                    }

                    string name = saioTypeName[(saioTypeName.LastIndexOf('.') + 1)..];
                    builder.AppendLine($"from .{TypeToFileName(name)} import {name}");
                }

                builder.AppendLine();
                builder.AppendLine($"class {type.Name}(ctypes.Structure):");

                foreach ((string name, string type, string hint) field in fields)
                {
                    builder.AppendLine($"    {field.name}: {field.hint}");
                }

                builder.AppendLine();
                builder.AppendLine($"{type.Name}._fields_ = [");

                foreach ((string name, string type, string hint) field in fields)
                {
                    builder.AppendLine($"    (\"{field.name}\", {field.type}),");
                }

                builder.AppendLine("]");
                builder.AppendLine();

                string filename = TypeToFileName(type.Name);
                initBuilder.AppendLine($"from .{filename} import {type.Name}");

                string filepath = Path.Join(outputDirectory, filename + ".py");
                File.WriteAllText(filepath, builder.ToString());
            }

            string initFilepath = Path.Join(outputDirectory, "__init__.py");
            File.WriteAllText(initFilepath, initBuilder.ToString());
        }
    
        public static void GenerateDLLFunction(string externalDirectory)
        {
            Type[] types = Assembly.GetAssembly(typeof(External.ExternC))!.GetTypes();

            StringBuilder builder = new();

            builder.AppendLine("# !!! GENERATED USING SAIO.NET.Utils !!!");
            builder.AppendLine("# Please do not touch manually!");
            builder.AppendLine("import ctypes");
            builder.AppendLine("from .. import nettypes, structs");
            builder.AppendLine();
            builder.AppendLine("FUNCTIONS = {");

            foreach (Type type in types)
            {
                foreach(MethodInfo method in type.GetMethods())
                {
                    if(method.GetCustomAttribute<UnmanagedCallersOnlyAttribute>() is not UnmanagedCallersOnlyAttribute attribute)
                    {
                        continue;
                    }

                    builder.AppendLine($"    \"{attribute.EntryPoint ?? method.Name}\": (");

                    ParameterInfo[] parameters = method.GetParameters();
                    if(parameters.Length > 0)
                    {
                        builder.AppendLine("        (");

                        foreach (ParameterInfo parameter in parameters)
                        {
                            if(!GetPythonType(parameter.ParameterType, "structs.", out string _, out string pythonType, out string _))
                            {
                                throw new InvalidOperationException($"Could not determine python type for parameter {parameter.ParameterType.Name} of {type.Name}: {parameter.ParameterType.FullName}");
                            }

                            builder.AppendLine($"            {pythonType},");
                        }

                        builder.AppendLine("        ),");
                    }
                    else
                    {
                        builder.AppendLine("        None,");
                    }

                    if(method.ReturnType != typeof(void))
                    {
                        if (!GetPythonType(method.ReturnType, "structs.", out string _, out string pythonType, out string _))
                        {
                            throw new InvalidOperationException($"Could not determine python return type for {type.Name}: {method.ReturnType.FullName}");
                        }

                        builder.AppendLine($"        {pythonType},");
                    }
                    else
                    {
                        builder.AppendLine("        None,");
                    }

                    if(type != typeof(ExternC))
                    {
                        builder.AppendLine("        \"NO ERROR CHECK\",");
                    }


                    builder.AppendLine("    ),");
                }
            }

            builder.AppendLine("}");

            string filepath = Path.Join(externalDirectory, "functions" ,"saio_net.py");
            File.WriteAllText(filepath, builder.ToString());
        }
	}
}
