using SA3D.Modeling.File;
using SA3D.Modeling.Mesh;
using SA3D.Modeling.Mesh.Buffer;
using SA3D.Modeling.Mesh.Weighted;
using SA3D.Modeling.ObjectData;
using SA3D.Modeling.ObjectData.Enums;
using SA3D.Modeling.Structs;
using System.IO;
using System.Linq;
using System.Numerics;

namespace SAIO.NET
{
    public class Model
    {
        public Node Root { get; }
        public WeightedMesh[] Attaches { get; }
        public bool Weighted { get; }
        public string Author { get; }
        public string Description { get; }

        public Model(Node root, WeightedMesh[] attaches, bool weighted, string author, string description)
        {
            Root = root;
            Attaches = attaches;
            Weighted = weighted;
            Author = author;
            Description = description;
        }

        public static Node ToNodeStructure(
            NodeStruct[] nodes,
            MeshStruct[] meshStructs,
            AttachFormat format,
            bool optimize,
            bool writeSpecular,
            bool autoNodeAttributes,
            bool flipVertexColorChannels)
        {
            if(nodes.Length == 0)
            {
                throw new InvalidDataException("No nodes passed over");
            }

            Node[] objNodes = new Node[nodes.Length];
            Node? lastRootSibling = null;

            for(int i = 0; i < nodes.Length; i++)
            {
                NodeStruct node = nodes[i];

                Matrix4x4 localMatrix = node.WorldMatrix;
                if(node.ParentIndex >= 0)
                {
                    Matrix4x4.Invert(nodes[node.ParentIndex].WorldMatrix, out Matrix4x4 invertedWorld);
                    localMatrix *= invertedWorld;
                }

                Matrix4x4.Decompose(localMatrix, out Vector3 scale, out Quaternion rotation, out Vector3 position);
                Vector3 euler = rotation.QuaternionToEuler(node.Attributes.HasFlag(NodeAttributes.RotateZYX));

                Node? parent = node.ParentIndex >= 0 ? objNodes[node.ParentIndex] : null;

                Node objNode = new()
                {
                    Label = node.Label
                };

                objNode.SetAllNodeAttributes(node.Attributes, RotationUpdateMode.Keep);
                objNode.UpdateTransforms(position, euler, scale);

                if(parent != null)
                {
                    parent.AppendChild(objNode);
                }
                else
                {
                    lastRootSibling?.InsertAfter(objNode);
                    lastRootSibling = objNode;
                }

                objNodes[i] = objNode;
            }

            Node root = objNodes[0];

            WeightedMesh[] meshes = new WeightedMesh[meshStructs.Length];
            for(int i = 0; i < meshStructs.Length; i++)
            {
                WeightedMesh mesh = meshStructs[i].ToWeightedBuffer(writeSpecular);

                if(flipVertexColorChannels)
                {
                    foreach(BufferCorner[] corners in mesh.TriangleSets)
                    {
                        for(int j = 0; j < corners.Length; j++)
                        {
                            Color color = corners[j].Color;
                            (color.Alpha, color.Blue) = (color.Blue, color.Alpha);
                            (color.Red, color.Green) = (color.Green, color.Red);
                            corners[j].Color = color;
                        }
                    }
                }

                meshes[i] = mesh;
            }


            WeightedMesh.ToModel(root, meshes, format, optimize);

            if(autoNodeAttributes)
            {
                foreach(Node node in objNodes)
                {
                    node.AutoNodeAttributes();
                }
            }

            return root;
        }

        public static Model Import(string filepath, bool optimize, bool flipVertexColors)
        {
            ModelFile file = ModelFile.ReadFromFile(filepath);
            return Process(file.Model, optimize, flipVertexColors, file.MetaData.Author ?? string.Empty, file.MetaData.Description ?? string.Empty);
        }

        public static Model Process(Node node, bool optimize, bool flipVertexColors = false, string author = "", string desription = "")
        {
            node.BufferMeshData(optimize);
            WeightedMesh[] meshes = WeightedMesh.FromModel(node, BufferMode.None);

            bool weighted = false;
            if(meshes.Length > 0)
            {
                weighted = meshes.Any(x => x.IsWeighted);

                // if no models are weighted, then blender wont create virtual meshes.
                // as such, an object should have just one model, to avoid creating non-virtual children
                if(!weighted)
                {
                    meshes = WeightedMesh.MergeAtRoots(meshes);
                }

                if(flipVertexColors)
                {
                    foreach(WeightedMesh mesh in meshes)
                    {
                        foreach(BufferCorner[] corners in mesh.TriangleSets)
                        {
                            for(int i = 0; i < corners.Length; i++)
                            {
                                Color color = corners[i].Color;
                                (color.Alpha, color.Blue) = (color.Blue, color.Alpha);
                                (color.Red, color.Green) = (color.Green, color.Red);
                                corners[i].Color = color;
                            }
                        }
                    }
                }
            }

            return new Model(node, meshes, weighted, author, desription);
        }
    }
}
