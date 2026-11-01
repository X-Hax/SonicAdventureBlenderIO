using SA3D.Modeling.ObjectData;
using SA3D.Modeling.ObjectData.Enums;
using SAIO.NET.Internal;
using System;
using System.Collections.Generic;
using System.Numerics;

namespace SAIO.NET.External.Structs
{
	public unsafe struct CNode
	{
		public char* label;
		public int parentIndex;
		public Matrix4x4 transform;

		public bool noAnimate;
		public bool noMorph;
		public bool clip;
		public bool cacheRotation;
		public bool applyCachedRotation;


		internal static CNode FromInternal(Node node, Dictionary<Node, int> nodeIndexLut)
		{
			return new()
			{
				label = Allocate.AllocString(node.Label),
				parentIndex = node.Parent == null ? -1 : nodeIndexLut[node.Parent],
				transform = node.LocalMatrix,

				noAnimate = node.NoAnimate,
				noMorph = node.NoMorph,
				clip = node.Clip,
				cacheRotation = node.CacheRotation,
				applyCachedRotation = node.ApplyCachedRotation
			};
		}

		internal static CNode* ArrayFromInternal(Node rootNode, out int resultSize)
		{
			Node[] nodes = rootNode.GetTreeNodes();

			CNode* result = Allocate.Alloc<CNode>(nodes.Length);
			resultSize = nodes.Length;

			Dictionary<Node, int> nodeIndexLut = [];

			for (int i = 0; i < nodes.Length; i++)
			{
				nodeIndexLut.Add(nodes[i], i);
				result[i] = FromInternal(nodes[i], nodeIndexLut);
			}

			return result;
		}

		internal readonly struct ToInternalContext
		{
			public readonly Node[] nodes;
			public readonly RotationMode rotationMode;

			public ToInternalContext(Node[] nodes, RotationMode rotationMode)
			{
				this.nodes = nodes;
				this.rotationMode = rotationMode;
			}
		}

		internal readonly Node ToInternal(ToInternalContext context)
		{
			Node result = new()
			{
				Label = Util.ToString(label) ?? throw new NullReferenceException("label is null"),
				NoAnimate = noAnimate,
				NoMorph = noMorph,
				UseQuaternionRotation = context.rotationMode == RotationMode.Quaternion,
				Clip = clip,
				CacheRotation = cacheRotation,
				ApplyCachedRotation = applyCachedRotation,
			};


			if(context.rotationMode == RotationMode.EulerZYX)
			{
				result.SetRotationZYX(true, RotationUpdateMode.Keep);
			}

			Matrix4x4.Decompose
				(transform,
				out Vector3 scale,
				out Quaternion quaternion,
				out Vector3 position
			);

			result.UpdateTransforms(position, quaternion, scale);

			if(parentIndex != -1)
			{
				context.nodes[parentIndex].AppendChild(result);
			}

			return result;
		}

		internal static Node ArrayToInternal(CNode* nodes, int nodesSize, RotationMode rotationMode)
		{
			Node[] resultNodes = new Node[nodesSize];
			ToInternalContext context = new(resultNodes, rotationMode);

			for(int i = 0; i < nodesSize; i++)
			{
				resultNodes[i] = nodes[i].ToInternal(context);
			}

			return resultNodes[0];
		}
	}
}
