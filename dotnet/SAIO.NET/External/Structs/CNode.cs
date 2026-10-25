using SA3D.Modeling.ObjectData;
using SA3D.Modeling.ObjectData.Enums;
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

		public bool noPosition;
		public bool noRotation;
		public bool noScale;
		public bool rotateZYX;
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

				noPosition = node.NoPosition,
				noRotation = node.NoRotation,
				noScale = node.NoScale,
				rotateZYX = node.RotateZYX,
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
			public readonly bool useQuaternions;

			public ToInternalContext(Node[] nodes, bool useQuaternions)
			{
				this.nodes = nodes;
				this.useQuaternions = useQuaternions;
			}
		}

		internal readonly Node ToInternal(ToInternalContext context)
		{
			Node result = new()
			{
				Label = Util.ToString(label) ?? throw new NullReferenceException("label is null"),
				NoPosition = noPosition,
				NoRotation = noRotation,
				NoScale = noScale,
				NoAnimate = noAnimate,
				NoMorph = noMorph,
				UseQuaternionRotation = context.useQuaternions,
				Clip = clip,
				CacheRotation = cacheRotation,
				ApplyCachedRotation = applyCachedRotation,
			};

			result.SetRotationZYX(rotateZYX, RotationUpdateMode.Keep);

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

		internal static Node ArrayToInternal(CNode* nodes, int nodesSize, bool useQuaternions)
		{
			Node[] resultNodes = new Node[nodesSize];
			ToInternalContext context = new(resultNodes, useQuaternions);

			for(int i = 0; i < nodesSize; i++)
			{
				resultNodes[i] = nodes[i].ToInternal(context);
			}

			return resultNodes[0];
		}
	}
}
