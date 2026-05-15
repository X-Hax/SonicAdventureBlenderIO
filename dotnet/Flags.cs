using SA3D.SA2Event.Model;
using SA3D.Modeling.ObjectData.Enums;
using System;
using System.Collections.Generic;
using System.Numerics;

namespace SAIO.NET
{
    public static class Flags
    {
        public static NodeAttributes ComposeNodeAttributes(
            bool noPosition,
            bool noRotation,
            bool noScale,
            bool skipDraw,
            bool skipChildren,
            bool rotateZYX,
            bool noAnimate,
            bool noMorph,
            bool clip,
            bool modifier,
            bool useQuaternionRotation,
            bool cacheRotation,
            bool applyCachedRotation,
            bool envelope)
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

            if(clip)
            {
                result |= NodeAttributes.Clip;
            }

            if(modifier)
            {
                result |= NodeAttributes.Modifier;
            }

            if(useQuaternionRotation)
            {
                result |= NodeAttributes.UseQuaternionRotation;
            }

            if(cacheRotation)
            {
                result |= NodeAttributes.CacheRotation;
            }

            if(applyCachedRotation)
            {
                result |= NodeAttributes.ApplyCachedRotation;
            }

            if(envelope)
            {
                result |= NodeAttributes.Envelope;
            }

            return result;
        }

        public static bool[] DecomposeNodeAttributes(this NodeAttributes attributes)
        {
            return [
                attributes.HasFlag(NodeAttributes.NoPosition),
                attributes.HasFlag(NodeAttributes.NoRotation),
                attributes.HasFlag(NodeAttributes.NoScale),
                attributes.HasFlag(NodeAttributes.SkipDraw),
                attributes.HasFlag(NodeAttributes.SkipChildren),
                attributes.HasFlag(NodeAttributes.RotateZYX),
                attributes.HasFlag(NodeAttributes.NoAnimate),
                attributes.HasFlag(NodeAttributes.NoMorph),
                attributes.HasFlag(NodeAttributes.Clip),
                attributes.HasFlag(NodeAttributes.Modifier),
                attributes.HasFlag(NodeAttributes.UseQuaternionRotation),
                attributes.HasFlag(NodeAttributes.CacheRotation),
                attributes.HasFlag(NodeAttributes.ApplyCachedRotation),
                attributes.HasFlag(NodeAttributes.Envelope)
            ];
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


        public static EventEntryAttribute ComposeEventEntryAttributes(
            bool hasEnvironment,
            bool noFogAndEasyDraw,
            bool light1,
            bool light2,
            bool light3,
            bool light4,
            bool modifierVolume,
            bool reflection,
            bool blare,
            bool useSimple)
        {
            EventEntryAttribute result = default;

            if(hasEnvironment)
            {
                result |= EventEntryAttribute.HasEnvironment;
            }

            if(noFogAndEasyDraw)
            {
                result |= EventEntryAttribute.NoFogAndEasyDraw;
            }

            if(light1)
            {
                result |= EventEntryAttribute.Light1;
            }

            if(light2)
            {
                result |= EventEntryAttribute.Light2;
            }

            if(light3)
            {
                result |= EventEntryAttribute.Light3;
            }

            if(light4)
            {
                result |= EventEntryAttribute.Light4;
            }

            if(modifierVolume)
            {
                result |= EventEntryAttribute.ModifierVolume;
            }

            if(reflection)
            {
                result |= EventEntryAttribute.Reflection;
            }

            if(blare)
            {
                result |= EventEntryAttribute.Blare;
            }

            if(useSimple)
            {
                result |= EventEntryAttribute.UseSimple;
            }

            return result;
        }

        public static bool[] DecomposeEventEntryAttributes(this EventEntryAttribute attributes)
        {
            return [
                attributes.HasFlag(EventEntryAttribute.HasEnvironment),
                attributes.HasFlag(EventEntryAttribute.NoFogAndEasyDraw),
                attributes.HasFlag(EventEntryAttribute.Light1),
                attributes.HasFlag(EventEntryAttribute.Light2),
                attributes.HasFlag(EventEntryAttribute.Light3),
                attributes.HasFlag(EventEntryAttribute.Light4),
                attributes.HasFlag(EventEntryAttribute.ModifierVolume),
                attributes.HasFlag(EventEntryAttribute.Reflection),
                attributes.HasFlag(EventEntryAttribute.Blare),
                attributes.HasFlag(EventEntryAttribute.UseSimple),
            ];
        }

    }
}