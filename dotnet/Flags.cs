using SA3D.SA2Event.Model;
using SA3D.Modeling.Mesh.Buffer;
using SA3D.Modeling.ObjectData.Enums;
using System;
using System.Collections.Generic;

namespace SAIO.NET
{
    public static class Flags
    {
        public static MaterialAttributes ComposeMaterialAttributes(bool flat, bool noAmbient, bool noDiffuse, bool noSpecular, bool useTexture, bool normalMapping)
        {
            MaterialAttributes result = default;

            if(flat)
            {
                result |= MaterialAttributes.Flat;
            }

            if(noAmbient)
            {
                result |= MaterialAttributes.NoAmbient;
            }

            if(noDiffuse)
            {
                result |= MaterialAttributes.NoLighting;
            }

            if(noSpecular)
            {
                result |= MaterialAttributes.NoSpecular;
            }

            if(useTexture)
            {
                result |= MaterialAttributes.UseTexture;
            }

            if(normalMapping)
            {
                result |= MaterialAttributes.NormalMapping;
            }

            return result;
        }

        public static bool[] DecomposeMaterialAttributes(this MaterialAttributes attributes)
        {
            return new[] {
                attributes.HasFlag(MaterialAttributes.Flat),
                attributes.HasFlag(MaterialAttributes.NoAmbient),
                attributes.HasFlag(MaterialAttributes.NoLighting),
                attributes.HasFlag(MaterialAttributes.NoSpecular),
                attributes.HasFlag(MaterialAttributes.UseTexture),
                attributes.HasFlag(MaterialAttributes.NormalMapping)
            };
        }


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


        public static GCEventEntryAttribute ComposeGCEventEntryAttributes(bool unk0, bool enableLight, bool unk2, bool disableShadow, bool unk4, bool unk5, bool unk6, bool reflection, bool blare, bool unk9)
        {
            GCEventEntryAttribute result = default;

            if(unk0)
            {
                result |= GCEventEntryAttribute.Unk0;
            }

            if(enableLight)
            {
                result |= GCEventEntryAttribute.Root_EnableLighting;
            }

            if(unk2)
            {
                result |= GCEventEntryAttribute.Unk2;
            }

            if(disableShadow)
            {
                result |= GCEventEntryAttribute.Root_DisableShadows;
            }

            if(unk4)
            {
                result |= GCEventEntryAttribute.Unk4;
            }

            if(unk5)
            {
                result |= GCEventEntryAttribute.Unk5;
            }

            if(unk6)
            {
                result |= GCEventEntryAttribute.Unk6;
            }

            if(reflection)
            {
                result |= GCEventEntryAttribute.Reflection;
            }

            if(blare)
            {
                result |= GCEventEntryAttribute.Blare;
            }

            if(unk9)
            {
                result |= GCEventEntryAttribute.Unk9;
            }

            return result;
        }

        public static bool[] DecomposeGCEventEntryAttributes(this GCEventEntryAttribute attributes)
        {
            return new[] {
                attributes.HasFlag(GCEventEntryAttribute.Unk0),
                attributes.HasFlag(GCEventEntryAttribute.Root_EnableLighting),
                attributes.HasFlag(GCEventEntryAttribute.Unk2),
                attributes.HasFlag(GCEventEntryAttribute.Root_DisableShadows),
                attributes.HasFlag(GCEventEntryAttribute.Unk4),
                attributes.HasFlag(GCEventEntryAttribute.Unk5),
                attributes.HasFlag(GCEventEntryAttribute.Unk6),
                attributes.HasFlag(GCEventEntryAttribute.Reflection),
                attributes.HasFlag(GCEventEntryAttribute.Blare),
                attributes.HasFlag(GCEventEntryAttribute.Unk9),
            };
        }

    }
}