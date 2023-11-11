using SA3D.Modeling.ModelData;
using SA3D.Modeling.ModelData.Weighted;
using SA3D.Modeling.ObjectData;
using SA3D.Modeling.Structs;
using System.Numerics;

namespace SAIO.NET
{
    public class Model
    {
        public Node Root { get; }
        public WeightedBufferAttach[] Attaches { get; }
        public bool Weighted { get; }
        public string Author { get; }
        public string Description { get; }

        public Model(Node root, WeightedBufferAttach[] attaches, bool weighted, string author, string description)
        {
            Root = root;
            Attaches = attaches;
            Weighted = weighted;
            Author = author;
            Description = description;
        }

        public static Node ToNodeStructure(
            NodeStruct[] nodes,
            MeshStruct[] weightedAttaches,
            AttachFormat format,
            bool optimize,
            bool ignoreWeights,
            bool ignoreRoot,
            bool writeSpecular,
            bool autoNodeAttributes)
        {
            if(nodes.Length == 0)
            {
                throw new InvalidDataException("No nodes passed over");
            }

            Node[] objNodes = new Node[nodes.Length];
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
                Vector3 euler = rotation.ToEuler(node.Attributes.HasFlag(NodeAttributes.RotateZYX));

                Node? parent = node.ParentIndex >= 0 ? objNodes[node.ParentIndex] : null;
                Node objNode = new(parent)
                {
                    Label = node.Label,
                    Position = position,
                    Rotation = euler,
                    Scale = scale
                };

                objNode.SetAllNodeAttributes(node.Attributes, true);

                objNodes[i] = objNode;
            }
            Node root = objNodes[0];
            if(ignoreRoot)
                root.VirtualParent = true;


            WeightedBufferAttach[] attaches = new WeightedBufferAttach[weightedAttaches.Length];
            for(int i = 0; i < weightedAttaches.Length; i++)
            {
                attaches[i] = weightedAttaches[i].ToWeightedBuffer(writeSpecular);
            }

            WeightedBufferAttach.ToModel(root, attaches, optimize, format, ignoreWeights);

            if(autoNodeAttributes)
            {
                foreach(Node node in objNodes)
                {
                    node.AutoNodeAttributes();
                }
            }

            return root;
        }

        public static Model Import(string filepath, bool optimize)
        {
            ModelFile file = ModelFile.Read(filepath);
            return Process(file.Model, optimize, file.MetaData.Author ?? "", file.MetaData.Description ?? "");
        }

        public static Model Process(Node node, bool optimize, string author = "", string desription = "")
        {
            node.BufferModel(optimize);
            WeightedBufferAttach[] attaches = WeightedBufferAttach.FromModel(node);
            bool weighted = attaches.Any(x => x.IsWeighted);

            // if no models are weighted, then blender wont create virtual meshes.
            // as such, an object should have just one model, to avoid creating non-virtual children
            if(!weighted)
                attaches = WeightedBufferAttach.MergeAtDependencyRoots(attaches, node.GetNodes());

            return new Model(node, attaches, weighted, author, desription);
        }
    }
}
