using SA3D.SA2Event.Model;
using SA3D.Modeling.Mesh.Buffer;
using SA3D.Modeling.ObjectData.Enums;
using System;
using System.Collections.Generic;

namespace SAIO.NET
{
    public static class Flags
    {
        public static NodeAttributes ComposeNodeAttributes(bool noPosition, bool noRotation, bool noScale, bool skipDraw, bool skipChildren, bool rotateZYX, bool noAnimate, bool noMorph)
        {
            NodeAttributes result = default;

            if(noPosition)
            {
                result |= NodeAttributes.NoPosition;
            }

            if(noRotation)
            {
                result |= NodeAttributes.NoRotation;
            }

            if(noScale)
            {
                result |= NodeAttributes.NoScale;
            }

            if(skipDraw)
            {
                result |= NodeAttributes.SkipDraw;
            }

            if(skipChildren)
            {
                result |= NodeAttributes.SkipChildren;
            }

            if(rotateZYX)
            {
                result |= NodeAttributes.RotateZYX;
            }

            if(noAnimate)
            {
                result |= NodeAttributes.NoAnimate;
            }

            if(noMorph)
            {
                result |= NodeAttributes.NoMorph;
            }

            return result;
        }

        public static bool[] DecomposeNodeAttributes(this NodeAttributes attributes)
        {
            return new[] {
                attributes.HasFlag(NodeAttributes.NoPosition),
                attributes.HasFlag(NodeAttributes.NoRotation),
                attributes.HasFlag(NodeAttributes.NoScale),
                attributes.HasFlag(NodeAttributes.SkipDraw),
                attributes.HasFlag(NodeAttributes.SkipChildren),
                attributes.HasFlag(NodeAttributes.RotateZYX),
                attributes.HasFlag(NodeAttributes.NoAnimate),
                attributes.HasFlag(NodeAttributes.NoMorph)
            };
        }


        public static SurfaceAttributes ComposeSurfaceAttributes(string[] names)
        {
            SurfaceAttributes result = default;

            for(int i = 0; i < names.Length; i++)
            {
                result |= Enum.Parse<SurfaceAttributes>(names[i]);
            }

            return result;
        }

        public static string[] DecomposeSurfaceAttributes(this SurfaceAttributes attributes)
        {
            SurfaceAttributes[] values = Enum.GetValues<SurfaceAttributes>();
            List<string> result = new();

            for(int i = 0; i < values.Length; i++)
            {
                SurfaceAttributes value = values[i];
                if(attributes.HasFlag(value))
                {
                    result.Add(value.ToString());
                }
            }

            return result.ToArray();
        }


        public static EventEntryAttribute ComposeEventEntryAttributes(bool unk0, bool enableLight, bool unk2, bool disableShadow, bool unk4, bool unk5, bool unk6, bool reflection, bool blare, bool unk9)
        {
            EventEntryAttribute result = default;

            if(unk0)
            {
                result |= EventEntryAttribute.Unk0;
            }

            if(enableLight)
            {
                result |= EventEntryAttribute.Root_EnableLighting;
            }

            if(unk2)
            {
                result |= EventEntryAttribute.Unk2;
            }

            if(disableShadow)
            {
                result |= EventEntryAttribute.Root_DisableShadows;
            }

            if(unk4)
            {
                result |= EventEntryAttribute.Unk4;
            }

            if(unk5)
            {
                result |= EventEntryAttribute.Unk5;
            }

            if(unk6)
            {
                result |= EventEntryAttribute.Unk6;
            }

            if(reflection)
            {
                result |= EventEntryAttribute.Reflection;
            }

            if(blare)
            {
                result |= EventEntryAttribute.Blare;
            }

            if(unk9)
            {
                result |= EventEntryAttribute.Unk9;
            }

            return result;
        }

        public static bool[] DecomposeEventEntryAttributes(this EventEntryAttribute attributes)
        {
            return new[] {
                attributes.HasFlag(EventEntryAttribute.Unk0),
                attributes.HasFlag(EventEntryAttribute.Root_EnableLighting),
                attributes.HasFlag(EventEntryAttribute.Unk2),
                attributes.HasFlag(EventEntryAttribute.Root_DisableShadows),
                attributes.HasFlag(EventEntryAttribute.Unk4),
                attributes.HasFlag(EventEntryAttribute.Unk5),
                attributes.HasFlag(EventEntryAttribute.Unk6),
                attributes.HasFlag(EventEntryAttribute.Reflection),
                attributes.HasFlag(EventEntryAttribute.Blare),
                attributes.HasFlag(EventEntryAttribute.Unk9),
            };
        }

    }
}