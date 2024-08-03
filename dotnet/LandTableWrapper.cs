using SA3D.Common;
using SA3D.Common.Lookup;
using SA3D.Modeling.Animation;
using SA3D.Modeling.File;
using SA3D.Modeling.Mesh;
using SA3D.Modeling.Mesh.Basic;
using SA3D.Modeling.Mesh.Weighted;
using SA3D.Modeling.ObjectData;
using SA3D.Modeling.ObjectData.Enums;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace SAIO.NET
{
    public class LandTableWrapper
    {
        public LandTable LandTable { get; }
        public MetaData MetaData { get; }
        public LandEntryStruct[] LandEntries { get; }
        public WeightedMesh[] Attaches { get; }
        public int? VisualCount { get; }

        public LandTableWrapper(LandTable landTable, MetaData metaData, LandEntryStruct[] landEntries, WeightedMesh[] attaches, int? visualCount)
        {
            LandTable = landTable;
            MetaData = metaData;
            LandEntries = landEntries;
            Attaches = attaches;
            VisualCount = visualCount;
        }

        private static void ExportSingle(
            LandTable landtable,
            LandEntryStruct[] landentries,
            WeightedMesh[] wbas,
            bool optimize,
            AutoNodeAttributeMode autoNodeAttributeMode)
        {
            AttachFormat attachFormat;
            switch(landtable.Format)
            {
                case ModelFormat.SA1:
                case ModelFormat.SADX:
                    attachFormat = AttachFormat.BASIC;
                    landtable.Attributes = LandtableAttributes.LoadTextureFile;
                    break;
                case ModelFormat.Buffer:
                    attachFormat = AttachFormat.Buffer;
                    break;
                default:
                    throw new InvalidOperationException($"Landtable format {landtable.Format} not a single mesh landtable");
            }

            Attach[] attaches = wbas.Select(x => x.ToAttach(attachFormat, optimize, out _)).ToArray();
            List<LandEntry> geometry = new();

            foreach(LandEntryStruct landentry in landentries)
            {
                Attach attach = attaches[landentry.MeshIndex];
                geometry.Add(landentry.ToLandEntry(attach, autoNodeAttributeMode));
            }

            landtable.Geometry = new LabeledArray<LandEntry>("geometry_" + StringExtensions.GenerateIdentifier(), geometry.ToArray());
        }

        private static void ExportDouble(
            LandTable landtable,
            LandEntryStruct[] landentries,
            WeightedMesh[] wbas,
            bool optimize,
            AutoNodeAttributeMode autoNodeAttributeMode)
        {
            AttachFormat attachFormat = landtable.Format switch
            {
                ModelFormat.SA2 => AttachFormat.CHUNK,
                ModelFormat.SA2B => AttachFormat.GC,
                _ => throw new InvalidOperationException($"Landtable format {landtable.Format} not a double mesh landtable"),
            };

            WeightedMesh?[] visualWBAs = new WeightedMesh?[wbas.Length];
            WeightedMesh?[] collisionWBAs = new WeightedMesh?[wbas.Length];

            List<LandEntryStruct> visualLandentries = new();
            List<LandEntryStruct> collisionLandentries = new();

            foreach(LandEntryStruct landentry in landentries)
            {
                bool isCollision = landentry.SurfaceAttributes.CheckIsCollision();
                bool isVisual = !isCollision || landentry.SurfaceAttributes.HasFlag(SurfaceAttributes.Visible);
                // if its neither, we'll just keep it as an invisible visual model. just in case

                if(isVisual)
                {
                    visualLandentries.Add(landentry);
                    visualWBAs[landentry.MeshIndex] = wbas[landentry.MeshIndex];
                }

                if(isCollision)
                {
                    collisionLandentries.Add(landentry);
                    collisionWBAs[landentry.MeshIndex] = wbas[landentry.MeshIndex];
                }
            }

            Attach?[] visualAttaches = visualWBAs.Select(x => x?.ToAttach(attachFormat, optimize, out _)).ToArray();
            Attach?[] collisionAttaches = collisionWBAs.Select(x => x?.ToAttach(AttachFormat.BASIC, optimize, out _)).ToArray();

            List<LandEntry> geometry = new();

            foreach(LandEntryStruct landentry in visualLandentries)
            {
                Attach attach = visualAttaches[landentry.MeshIndex] ?? throw new InvalidOperationException($"Attach {landentry.MeshIndex} was not converted as visual");
                LandEntry le = landentry.ToLandEntry(attach, autoNodeAttributeMode);
                le.SurfaceAttributes &= SurfaceAttributes.VisualMask;
                geometry.Add(le);
            }

            foreach(LandEntryStruct landentry in collisionLandentries)
            {
                Attach attach = collisionAttaches[landentry.MeshIndex] ?? throw new InvalidOperationException($"Attach {landentry.MeshIndex} was not converted as collision");
                LandEntry le = landentry.ToLandEntry(attach, autoNodeAttributeMode);
                le.SurfaceAttributes &= SurfaceAttributes.CollisionMask;
                geometry.Add(le);
            }

            landtable.Geometry = new LabeledArray<LandEntry>("collist_" + StringExtensions.GenerateIdentifier(), geometry.ToArray());
        }

        public static LandTable ProcessLandtable(
            LandEntryStruct[] landentries,
            MeshStruct[] weightedAttaches,
            LandEntryMotion[] motions,
            ModelFormat format,
            string name,
            float drawDistance,
            string texFileName,
            uint texListPointer,
            bool optimize,
            bool writeSpecular,
            bool fallbackSurfaceAttributes,
            AutoNodeAttributeMode autoNodeAttributeMode,
            bool ensurePositiveEulerAngles)
        {
            if(landentries.Length == 0)
            {
                throw new InvalidDataException("No landentries passed over");
            }

            LandTable landtable = new(new LabeledArray<LandEntry>(0), format)
            {
                Label = name,
                DrawDistance = drawDistance,
                TextureFileName = string.IsNullOrWhiteSpace(texFileName) ? null : texFileName,
                TexListPtr = texListPointer
            };

            WeightedMesh[] wbas = weightedAttaches
                .Select(x => x.ToWeightedBuffer(writeSpecular))
                .ToArray();

            if(fallbackSurfaceAttributes)
            {
                for(int i = 0; i < landentries.Length; i++)
                {
                    if((landentries[i].SurfaceAttributes & SurfaceAttributes.ValidMask) == default)
                    {
                        landentries[i].SurfaceAttributes = SurfaceAttributes.Visible | SurfaceAttributes.Solid;
                    }
                }
            }

            switch(format)
            {
                case ModelFormat.Buffer:
                case ModelFormat.SA1:
                case ModelFormat.SADX:
                    ExportSingle(landtable, landentries, wbas, optimize, autoNodeAttributeMode);
                    break;
                case ModelFormat.SA2:
                case ModelFormat.SA2B:
                    ExportDouble(landtable, landentries, wbas, optimize, autoNodeAttributeMode);
                    break;
            }

            if(motions.Length > 0)
            {
                landtable.GeometryAnimations = new LabeledArray<LandEntryMotion>("animlist_" + landtable.Label, motions);
            }

            if(ensurePositiveEulerAngles)
            {
                foreach(LandEntry landEntry in landtable.Geometry)
                {
                    landEntry.Model.EnsurePositiveEulerAnglesTree();
                }

                foreach(LandEntryMotion landEntryMotion in landtable.GeometryAnimations)
                {
                    landEntryMotion.Model.EnsurePositiveEulerAnglesTree();
                }
            }

            return landtable;
        }

        public static void Export(
            LandEntryStruct[] landentries,
            MeshStruct[] weightedAttaches,
            LandEntryMotion[] motions,
            ModelFormat format,
            string name,
            float drawDistance,
            string texFileName,
            uint texListPointer,
            string filepath,
            bool optimize,
            bool writeSpecular,
            bool fallbackSurfaceAttributes,
            AutoNodeAttributeMode autoNodeAttributeMode,
            bool ensurePositiveEulerAngles,
            string author,
            string description)
        {
            LandTable landtable = ProcessLandtable(
                landentries,
                weightedAttaches,
                motions,
                format,
                name,
                drawDistance,
                texFileName,
                texListPointer,
                optimize,
                writeSpecular,
                fallbackSurfaceAttributes,
                autoNodeAttributeMode,
                ensurePositiveEulerAngles);

            MetaData metaData = new()
            {
                Author = author,
                Description = description
            };

            LevelFile.WriteToFile(filepath, landtable, metaData);
        }

        public static LandTableWrapper Import(string filepath, bool optimize)
        {
            LevelFile level = LevelFile.ReadFromFile(filepath);

            Dictionary<Attach, int> attaches = new();
            List<LandEntryStruct> landEntries = new();

            int? visualCount = null;

            foreach(LandEntry landEntry in level.Level.Geometry)
            {
                if(landEntry.Model.Attach == null)
                {
                    Console.WriteLine($"Landentry {landEntry.Model.Label} did not have a model");
                    continue;
                }

                if(level.Level.Format >= ModelFormat.SA2
                    && landEntry.Model.Attach is BasicAttach
                    && visualCount == null)
                {
                    visualCount = landEntries.Count;
                }

                if(!attaches.TryGetValue(landEntry.Model.Attach, out int index))
                {
                    index = attaches.Count;
                    attaches.Add(landEntry.Model.Attach, index);
                }

                landEntries.Add(new(
                    landEntry.Model.Label,
                    index,
                    landEntry.BlockBit,
                    landEntry.Model.Attributes,
                    landEntry.SurfaceAttributes,
                    landEntry.Model.LocalMatrix));
            }

            level.Level.BufferMeshData(optimize);

            WeightedMesh[] wbas = new WeightedMesh[attaches.Count];
            foreach(KeyValuePair<Attach, int> item in attaches)
            {
                wbas[item.Value] = WeightedMesh.FromAttach(item.Key, BufferMode.None);
            }

            return new(
                level.Level, 
                level.MetaData, 
                landEntries.ToArray(), 
                wbas, 
                visualCount);
        }

    }
}
