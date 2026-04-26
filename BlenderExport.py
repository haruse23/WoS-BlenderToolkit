from .Model import *
from .BlenderMesh import *
from .Hash import *
from .Helpers import *
from .Wrap import *

from .Skeleton import *

from mathutils import Matrix, Vector, Quaternion
import bpy
import io









def ExportModel(collection, filepath, mesh_objects):
    with open(filepath, "wb") as out:
    
        if collection is None:
            raise ValueError("Collection is None!")
            
        mesh_count = len(mesh_objects)
        
        data = FetchBlenderData(mesh_objects)
        
        scene = bpy.context.scene
             
        ############################################################
        # Writing Wrap Section (Header)
        wrap_header_start = out.tell()
        
        wrap_header = WRAPSectionHeader()
        
        wrap_header.dwMagic = 1346458199 # WRAP bytes in decimal, interpreted as 4-byte unsigned int
        
        wrap_header.dwPatchTablePointer = 0x28
        
        wrap_header.dwComponentCount = 2
        wrap_header.dwComponentsPointer = 0x4
       
        
        PatchTablePointerStart, IMGPointerStart, PHYSPointerStart = wrap_header.WriteWRAPSectionHeader(out)
       
       
       
       
       
        # Writing WRAP Section (PatchTable)
        wrap_patchtable_start = out.tell()
        
        wrap_patchtable = WRAPSectionPatchTable()
        

        wrap_patchtable.dwExternalPatchCount = 1
        wrap_patchtable.dwExternalPatchPointer = 0x1C
        
        wrap_patchtable.dwInternalPatchCount = 1 + mesh_count * 5
        wrap_patchtable.dwGlobalPatchCount = 0
        
        has_materials = []
        for mesh_obj in mesh_objects:
            if any(slot.material for slot in mesh_obj.material_slots):
                wrap_patchtable.dwExternalPatchCount += 1
                has_materials.append(True)
            else:
                has_materials.append(False)
                
        
        has_armature = [False, -1]
        for m, mesh_obj in enumerate(mesh_objects):
            if not has_armature[0] and mesh_obj.parent and mesh_obj.parent.type == 'ARMATURE':
                wrap_patchtable.dwExternalPatchCount += 1 # Add Skel External Patch Pointer if at least one mesh has a parent armature, then stop for this one
                has_armature[0] = True
                has_armature[1] = m
                
            if mesh_obj.parent and mesh_obj.parent.type == 'ARMATURE':
                wrap_patchtable.dwInternalPatchCount += 1 # Add BonePalettePointer Internal Patch Pointer as many times as mesh count, regardles
                
        ExternalPatchPointerStart, InternalPatchPointerStart, GlobalPatchPointerStart = wrap_patchtable.WriteWRAPSectionPatchTable(out)
        
        # Writing WRAP Section (ExternalPatch)
        wrap_external_start = out.tell()
        
        wrap_external = WRAPSectionExternalPatch()
        
        for _ in range(wrap_patchtable.dwExternalPatchCount):
            wrap_external.WriteWRAPSectionExternalPatch(out)
        
        
        # Writing WRAP Section (InternalPatch)
        wrap_internal_start = out.tell()
        
        wrap_internal = WRAPSectionInternalPatch()
        
        for __ in range(wrap_patchtable.dwInternalPatchCount):
            wrap_internal.WriteWRAPSectionInternalPatch(out)
            
        write_alignment_16_A1(out, out.tell())
        
        
        ################################################
        model_bounds = data["model_bounds"]
        
        
        # Model Header
        
        model_header = ModelHeader()
        
        model_header.dwFilenameHash = Hash(collection.name)
        model_header.dwMeshCount = mesh_count
        
        model_header.ModelBoundingSphereRadius = model_bounds["model_bsphere_radius"]
        
        model_header.fpModelBBoxX = model_bounds["ModelBBox"][0]
        model_header.fpModelBBoxY = model_bounds["ModelBBox"][1]
        model_header.fpModelBBoxZ = model_bounds["ModelBBox"][2]
        model_header.fpModelBBoxW = 0
        

        model_header_start = out.tell()
        MeshTablePointerStart = model_header.WriteModelHeader(out)
            
        out.write(bytes.fromhex("BB 32 87 07 CA 2F 00 00 00 00 00 00 B0 01 00 00")) # Preserved before Model Table
        
        
        
        
        
        # Model Table
        mesh_table = MeshTable()
        
        mesh_table_start = out.tell()
        for obj in collection.objects:
            if obj.type != "MESH":
                continue
            
            
                
            mesh_table.WriteMeshTable(out)
            
        #write_alignment_16(out, out.tell())
       
        # MeshInfo, SchemaTable, VertexSchema
        mesh_info_pos = []
        bone_palette_pos = []
        bone_indices = []
        
        first_vertex_schema_pos = []
        
        mesh_info = MeshInfo()
        schema_table = SchemaTable()
        vertex_schema = VertexSchema()
        meshes_data = data["meshes"] # mesh_data_list, List of each mesh data (List of dictionaries for every mesh)
        
        
        mesh_info_start_list = []
        
        schema_table_start_list = []
        
        for n, obj in enumerate(mesh_objects):
            # Writing Mesh Info
            mesh_info_start_list.append(out.tell())
            
            
            
            mesh_data = meshes_data[n] # Data of Mesh number n
            

            mesh_info.WriteMeshInfo(out)
            
            out.write(bytes.fromhex("04 00 00 00 01 00 00 00")) # Preserved (PrimitiveType [4, TriangeList or 5, TriangleStrips] + Unknown)
            

            # Writing Bone Palette
            mesh_dict = mesh_data["data"]
            
            BonePaletteCount = get_bone_palette_count(mesh_dict["blend_indices"], mesh_dict["blend_weights"])
  
            bone_data = mesh_data["bone_data"]
            
            palette = bone_data["bone_palette"]
            
            for bone_index in palette:
                write_ushort(out, bone_index)
            
            
           
                

            
            
            # Writing Schema Table
            vertex_schema_data = mesh_data["attributes"] # Dictionary of attributes (list), offset (list), type (list), usage (list)
            
            schema_table.dwVertexStride = vertex_schema_data["attributes"][0][1] # Size of Each Vertex's Data in Bytes
            schema_table.dwVertexSchemaPointer = 0x8
            
            schema_table_start_list.append(out.tell())
            
            schema_table.WriteSchemaTable(out)
            
            
            
            
            
        
            # Writing Vertex Schema
            for a in range(vertex_schema_data["attributes"][0][0]): # Iterating over the Number of Vertex Attributes
                vertex_schema.wOffset = vertex_schema_data["offset"][a] # Offset of Each Attribute in the Vertex Stride
                
                vertex_schema.bType = vertex_schema_data["type"][a] # Data type of Each Attribute
                
                vertex_schema.bUsage = vertex_schema_data["usage"][a] # Usage of Each Attribute
                
                vertex_schema.bUsageIndex = vertex_schema_data["usage_index"][a] # Usage Index of Each Attribute
                
                vertex_schema.WriteVertexSchema(out)
            
            out.write(b'\xFF\x00\x00\x00\x11\x00\x00\x00') # Vertex Schema Sentinel
            #write_alignment_16(out, out.tell())
            
        
        
        
        
        
        # Write "PHYS"
        out.write(b'PHYS')
        
        # Vertex Buffer & Index Buffer
        vertex_buffer_start_list = []
        index_buffer_start_list = []
        for m in range(mesh_count):

            mesh_data = meshes_data[m] # Data of Mesh number m
            
            mesh_dict = mesh_data["data"]
            
            vertex_count = mesh_data["vertex_count"]
            
            positions = mesh_dict["positions"]
            normals = mesh_dict["normals"]
            tangents = mesh_dict["tangents"]
            binormals = mesh_dict["binormals"]
            
            uvs = mesh_dict["uvs"]

            
            
            colors = mesh_dict["colors"]
            blend_indices = mesh_dict["blend_indices"]
            blend_weights = mesh_dict["blend_weights"]
            
            ModelBBox = model_bounds["ModelBBox"]
            
            bone_data = mesh_data["bone_data"]
            
            BonePaletteCount = len(bone_data["bone_palette"])
           
            vertex_attribute = VertexAttribute()
            
            vertex_buffer_start_list.append(out.tell())
            
            vertex_attribute.WriteVertexAttribute(out, vertex_count, positions, normals, tangents, binormals, uvs, colors, blend_indices, blend_weights, ModelBBox, BonePaletteCount) 

            write_alignment_4(out, out.tell()) # write 4-byte alignment after vertex buffer
            
            triangles = mesh_dict["triangle_list"]
            
            
            index_buffer = IndexBuffer()
            
            index_buffer_start_list.append(out.tell())
            
            index_buffer.Indices = [i for tri in triangles for i in tri]
            
            if scene.reverse_winding_order:
                index_buffer.Indices = reverse_winding_order_export(index_buffer.Indices)
            
            index_buffer.WriteIndices(out, vertex_count)
            
            write_alignment_4(out, out.tell()) # write 4-byte alignment after index buffer
            
        
        
        end_of_file = out.tell()

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        # Updating & Rewriting WRAP Section (Header)
        out.seek(wrap_header_start)
        
        wrap_header.dwIMGSize = vertex_buffer_start_list[0] - model_header_start - 4
        wrap_header.dwIMGPointer = model_header_start - IMGPointerStart
        
        wrap_header.dwPHYSSize = end_of_file - vertex_buffer_start_list[0]
        wrap_header.dwPHYSPointer = vertex_buffer_start_list[0] - PHYSPointerStart
        
        wrap_header.WriteWRAPSectionHeader(out)
        
        
        # Updating & Rewriting WRAP Section (PatchTable)
        out.seek(wrap_patchtable_start)
        # ExternalPatchPointer is fixed -- 0x1C
        
        wrap_patchtable.dwInternalPatchPointer = wrap_internal_start - InternalPatchPointerStart
        wrap_patchtable.dwGlobalPatchPointer = model_header_start - GlobalPatchPointerStart
        
        wrap_patchtable.WriteWRAPSectionPatchTable(out)
        
        
        # Updating & Rewriting WRAP Section (ExternalPatch)
        out.seek(wrap_external_start)
        
        # NAME
        wrap_external.dwPatchToTypeExternal = 1162690894 # NAME bytes in decimal, interpreted as 4-byte unsigned int
        wrap_external.dwExternalFilenameHash = b"\x00\x00\x00\x00"
        wrap_external.dwExpectedIndexExternal = 4294967295 # FF FF FF FF bytes in decimal, interpreted as 4-byte unsigned int
        wrap_external.dwPointerTargetExternal = model_header_start - wrap_external.PointerTargetExternalStartList[0]
        
        wrap_external.WriteWRAPSectionExternalPatch(out)
        
        # SKEL
        if has_armature[0]: # if True
            index = has_armature[1]
            mesh_data = meshes_data[index]
            skeleton_name = Hash(mesh_data["skeleton_name"]).to_bytes(4, byteorder="little")

            wrap_external.dwPatchToTypeExternal = 1279609683 # SKEL bytes in decimal, interpreted as 4-byte unsigned int
            wrap_external.dwExternalFilenameHash = skeleton_name
            wrap_external.dwExpectedIndexExternal = 4294967295 # FF FF FF FF bytes in decimal, interpreted as 4-byte unsigned int
            wrap_external.dwPointerTargetExternal = (model_header_start + 20) - wrap_external.PointerTargetExternalStartList[1]

            wrap_external.WriteWRAPSectionExternalPatch(out)
            
        # MAT
        for t, hm in enumerate(has_materials):
            mesh_data = meshes_data[t]
            
            if hm: # if True
                material_name = bytes.fromhex(mesh_data["material_name"].replace("0x", ""))[::-1]

                wrap_external.dwPatchToTypeExternal = 5521741 # MAT bytes in decimal, interpreted as 4-byte unsigned int
                wrap_external.dwExternalFilenameHash = material_name
                wrap_external.dwExpectedIndexExternal = 4294967295 # FF FF FF FF bytes in decimal, interpreted as 4-byte unsigned int
            
                if has_armature[0]: # if True
                    wrap_external.dwPointerTargetExternal = mesh_info.MaterialDataPointerStart[t] - wrap_external.PointerTargetExternalStartList[t+2]
                    
                else:
                    wrap_external.dwPointerTargetExternal = mesh_info.MaterialDataPointerStart[t] - wrap_external.PointerTargetExternalStartList[t+1]
                
                wrap_external.WriteWRAPSectionExternalPatch(out)
            
            
        
        # Updating & Rewriting WRAP Section (InternalPatch)
        out.seek(wrap_internal_start)
        wrap_internal.dwPointerTargetInternal = (model_header_start + 16) - wrap_internal.PointerTargetInternalStartList[0] # First Internal Pointer, MeshTablePointer
        
        wrap_internal.WriteWRAPSectionInternalPatch(out)
        
        m = 0
        i = 1
        for base in range(mesh_count):
            mesh_data = meshes_data[base]
            
            bone_data = mesh_data["bone_data"]
                    
            wrap_internal.dwPointerTargetInternal = mesh_table.MeshInfoPointerStart[m] - wrap_internal.PointerTargetInternalStartList[i] # Second Internal Pointer, MeshInfoPointer
        
            wrap_internal.WriteWRAPSectionInternalPatch(out)
            
            i+=1
            
            BonePaletteCount = len(bone_data["bone_palette"])
            if BonePaletteCount:
                wrap_internal.dwPointerTargetInternal = mesh_info.BonePalettePointerStart[m] - wrap_internal.PointerTargetInternalStartList[i] # Third Internal Pointer, BonePalettePointer
            
                wrap_internal.WriteWRAPSectionInternalPatch(out)
                
                i+=1
            
            wrap_internal.dwPointerTargetInternal = mesh_info.VertexBufferPointerStart[m] - wrap_internal.PointerTargetInternalStartList[i] # Fourth Internal Pointer, VertexBufferPointer
        
            wrap_internal.WriteWRAPSectionInternalPatch(out)
            
            i+=1
        
            wrap_internal.dwPointerTargetInternal = mesh_info.IndexBufferPointerStart[m] - wrap_internal.PointerTargetInternalStartList[i] # Fifth Internal Pointer, IndexBufferPointer
        
            wrap_internal.WriteWRAPSectionInternalPatch(out)
            
            i+=1
        
            wrap_internal.dwPointerTargetInternal = mesh_info.SchemaTablePointerStart[m] - wrap_internal.PointerTargetInternalStartList[i] # Sixth Internal Pointer, SchemaTablePointer
        
            wrap_internal.WriteWRAPSectionInternalPatch(out)
            
            i+=1
        
            wrap_internal.dwPointerTargetInternal = schema_table.VertexSchemaPointerStart[m] - wrap_internal.PointerTargetInternalStartList[i] # Seventh Internal Pointer, VertexSchemaPointer
        
            wrap_internal.WriteWRAPSectionInternalPatch(out)
            
            i+=1
            
            m += 1
          
            
            
            
            
            
            
        
        # Updating & Rewriting Model Header
        out.seek(model_header_start)
        
        model_header.dwMeshTablePointer = mesh_table_start - MeshTablePointerStart # Subtract absolute offset of MeshTablePointer from absolute offset of MeshTable for each mesh
        # The Result should be the relative offset (MeshTablePointer)
    
        model_header.WriteModelHeader(out)
        
        
        # Updating & Rewriting Mesh Table\
        out.seek(mesh_table_start)
        for m in range(mesh_count):
            
            
            mesh_table.dwMeshInfoPointer = mesh_info_start_list[m] - mesh_table.MeshInfoPointerStart[m] # Subtract absolute offset of MeshInfoPointer from absolute offset of MeshInfo for each mesh
            # The Result should be the relative offset (MeshInfoPointer)
            
            mesh_table.WriteMeshTable(out)
            
            
            
        # Rewriting and Filling in Mesh Info
        
        for m in range(mesh_count):
            out.seek(mesh_info_start_list[m]) # Seek to Mesh number m's mesh_info
            
            mesh_data = meshes_data[m]
            
            bounds = mesh_data["bounds"]
                
            mesh_dict = mesh_data["data"]
            
            bone_data = mesh_data["bone_data"]
            
            mesh_info.MeshBoundingSphereRadius = bounds["mesh_bsphere_radius"]
            
            mesh_info.fpMeshBBoxX = bounds["MeshBBox"][0]
            mesh_info.fpMeshBBoxY = bounds["MeshBBox"][1]
            mesh_info.fpMeshBBoxZ = bounds["MeshBBox"][2]
            mesh_info.fpMeshBBoxW = 0
            
            BonePaletteCount = len(bone_data["bone_palette"])
            
            if BonePaletteCount:
                mesh_info.dwBonePalettePointer = 0x34
            
            
            mesh_info.dwBonePaletteIndexCount = BonePaletteCount
            
            mesh_info.dwVertexBufferPointer = vertex_buffer_start_list[m] - mesh_info.VertexBufferPointerStart[m] # Subtract absolute offset of VertexBufferPointer from absolute offset of VertexBuffer for each mesh
            # The Result should be the relative offset (VertexBufferPointer)
            
            mesh_info.dwVertexCount = mesh_data["vertex_count"]
            
            mesh_info.dwIndexBufferPointer = index_buffer_start_list[m] - mesh_info.IndexBufferPointerStart[m] # Subtract absolute offset of IndexBufferPointer from absolute offset of IndexBuffer for each mesh
            # The Result should be the relative offset (IndexBufferPointer)
            
            mesh_info.dwIndexCount = len(mesh_data["triangles"]) * 3
            
            if mesh_info.dwVertexCount > 65535: # Setting Index Size
                mesh_info.dwIndexSize = 4  # 32-bit
            else:
                mesh_info.dwIndexSize = 2  # 16-bit
                
            
            mesh_info.dwSchemaTablePointer = schema_table_start_list[m] - mesh_info.SchemaTablePointerStart[m] # Subtract absolute offset of SchemaTablePointer from absolute offset of SchemaTable for each mesh
            # The Result should be the relative offset (SchemaTablePointer)

                
            mesh_info.WriteMeshInfo(out)
        
        
        
        
        


def ExportSkeleton(filepath, armature):
    with open(filepath, "wb") as out:
        skeleton_name = armature.name
        bone_count = len(armature.data.bones)

        bones = list(armature.data.bones)
        bone_index = {b.name: i for i, b in enumerate(bones)}
        
        
        ############################################################
        # Writing Wrap Section (Header)
        wrap_header_start = out.tell()
        
        wrap_header = WRAPSectionHeader()
        
        wrap_header.dwMagic = 1346458199 # WRAP bytes in decimal, interpreted as 4-byte unsigned int
        
        wrap_header.dwPatchTablePointer = 0x18
        
        wrap_header.dwComponentCount = 1
        wrap_header.dwComponentsPointer = 0x4
       
        
        PatchTablePointerStart, IMGPointerStart, PHYSPointerStart = wrap_header.WriteWRAPSectionHeader(out)


        # Writing WRAP Section (PatchTable)
        wrap_patchtable_start = out.tell()
        
        wrap_patchtable = WRAPSectionPatchTable()
        

        wrap_patchtable.dwExternalPatchCount = bone_count
        wrap_patchtable.dwExternalPatchPointer = 0x1C
        
        wrap_patchtable.dwInternalPatchCount = 1
        wrap_patchtable.dwGlobalPatchCount = 0
        
        ExternalPatchPointerStart, InternalPatchPointerStart, GlobalPatchPointerStart = wrap_patchtable.WriteWRAPSectionPatchTable(out)
        
        
        # Writing WRAP Section (ExternalPatch)
        wrap_external_start = out.tell()
        
        wrap_external = WRAPSectionExternalPatch()
        
        for _ in range(wrap_patchtable.dwExternalPatchCount):
            wrap_external.WriteWRAPSectionExternalPatch(out)
        
        
        # Writing WRAP Section (InternalPatch)
        wrap_internal_start = out.tell()
        
        wrap_internal = WRAPSectionInternalPatch()
        
        for __ in range(wrap_patchtable.dwInternalPatchCount):
            wrap_internal.WriteWRAPSectionInternalPatch(out)
            
        write_alignment_16_A1(out, out.tell())
        
        
        # Skeleton File Start
        skeleton_header_start = out.tell()
        
        skeleton_header = SkeletonHeader()
  
        skeleton_header.FilenameHash = Hash(skeleton_name)
        skeleton_header.BoneCount = bone_count
        skeleton_header.SkeletonDataStartPointer = 0x4
        
        skeleton_header.WriteSkeletonHeader(out)

        skeleton_data = SkeletonData()
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in armature.data.edit_bones:
            
            
            unknown_data = """00 00 80 3F 00 00 00 00 00 00 00 00 00 00 00 00
            00 00 00 00 00 00 80 3F 00 00 00 00 00 00 00 00
            00 00 00 00 00 00 00 00 00 00 80 3F 00 00 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"""
            
            skeleton_data.UnknownData = bytes.fromhex(unknown_data)
            
            
            bind_pose = bone.matrix
            
            # Invert to get inverse bind pose and transpose to get row-major order for the game
            inverse_bind_pose = bind_pose.inverted()
            inverse_bind_pose.transpose()
            
            """Required Shape for Export (Game's row-major)
            Matrix((  
            (bone.rotX1, bone.rotX2, bone.rotX3, 0.0),
            (bone.rotY1, bone.rotY2, bone.rotY3, 0.0),
            (bone.rotZ1, bone.rotZ2, bone.rotZ3, 0.0),
            (bone.pos_x, bone.pos_y, bone.pos_z, 1.0)
            ))"""
            
            
           
            
            skeleton_data.rotX1 = inverse_bind_pose[0][0]
            skeleton_data.rotX2 = inverse_bind_pose[0][1]
            skeleton_data.rotX3 = inverse_bind_pose[0][2]
            
            skeleton_data.rotY1 = inverse_bind_pose[1][0]
            skeleton_data.rotY2 = inverse_bind_pose[1][1]
            skeleton_data.rotY3 = inverse_bind_pose[1][2]
            
            
            skeleton_data.rotZ1 = inverse_bind_pose[2][0]
            skeleton_data.rotZ2 = inverse_bind_pose[2][1]
            skeleton_data.rotZ3 = inverse_bind_pose[2][2]
            
            skeleton_data.pos_x = inverse_bind_pose[3][0]
            skeleton_data.pos_y = inverse_bind_pose[3][1]
            skeleton_data.pos_z = inverse_bind_pose[3][2]
            skeleton_data.Unknown4 = 1.0
            
            values = [skeleton_data.rotX1, skeleton_data.rotX2, skeleton_data.rotX3, skeleton_data.Unknown1,
            skeleton_data.rotY1, skeleton_data.rotY2, skeleton_data.rotY3, skeleton_data.Unknown2,
            skeleton_data.rotZ1, skeleton_data.rotZ2, skeleton_data.rotZ3, skeleton_data.Unknown3,
            skeleton_data.pos_x, skeleton_data.pos_y, skeleton_data.pos_z, skeleton_data.Unknown4]
            
            matrix_data = bytearray()
            
            for v in values:
                matrix_data += struct.pack('<f', v)
                
            skeleton_data.InverseBindPoseMatrix = matrix_data
            
            bone_name = bone.name
            skeleton_data.BonenameHash = Hash(bone_name)
            
            bone_parentindex = bone_index[bone.parent.name] if bone.parent else -1
            skeleton_data.BoneParentIndex = bone_parentindex
            
            skeleton_data.WriteSkeletonData(out)
            
            
        end_of_file = out.tell()
            
        # Updating & Rewriting WRAP Section (Header)
        out.seek(wrap_header_start)
        
        wrap_header.dwIMGSize = end_of_file - skeleton_header_start
        wrap_header.dwIMGPointer = skeleton_header_start - IMGPointerStart

        wrap_header.WriteWRAPSectionHeader(out)
        
        
        # Updating & Rewriting WRAP Section (PatchTable)
        out.seek(wrap_patchtable_start)
        # ExternalPatchPointer is fixed -- 0x1C
        
        wrap_patchtable.dwInternalPatchPointer = wrap_internal_start - InternalPatchPointerStart
        wrap_patchtable.dwGlobalPatchPointer = skeleton_header_start - GlobalPatchPointerStart
        
        wrap_patchtable.WriteWRAPSectionPatchTable(out)
        
        
        # Updating & Rewriting WRAP Section (ExternalPatch)
        out.seek(wrap_external_start)
        
        # NAME (Bone Name)
        for i in range(bone_count):
            wrap_external.dwPatchToTypeExternal = 1162690894 # NAME bytes in decimal, interpreted as 4-byte unsigned int
            wrap_external.dwExternalFilenameHash = b"\x00\x00\x00\x00"
            wrap_external.dwExpectedIndexExternal = 4294967295 # FF FF FF FF bytes in decimal, interpreted as 4-byte unsigned int
            wrap_external.dwPointerTargetExternal = skeleton_data.BonenamePointerStartList[i] - wrap_external.PointerTargetExternalStartList[i]
            
            wrap_external.WriteWRAPSectionExternalPatch(out)
            
        
        
        # Updating & Rewriting WRAP Section (InternalPatch)
        out.seek(wrap_internal_start)
        wrap_internal.dwPointerTargetInternal = (skeleton_header_start + 12) - wrap_internal.PointerTargetInternalStartList[0] # First and Only Internal Pointer, SkeletonDataStartPointer
        
        wrap_internal.WriteWRAPSectionInternalPatch(out)
        
        write_alignment_16_A1(out, out.tell())
            


        ##########################################
        
        # UNUSED SECTION, YOU CAN IGNORE IT

        ##########################################

        """# WRAPSection
        WRAPHeaderAndPatch = io.BytesIO()
        WRAPExternalPatch = io.BytesIO()
        WRAPInternalPatch = io.BytesIO()
        
        
        wrap = WRAPSection()
        
        wrap.WriteWRAPSectionHeaderAndPatchTable(WRAPHeaderAndPatch)
        
        pointerTargetPOSListExt = wrap.WriteWRAPSectionExternalPatch(WRAPExternalPatch)
        
        wrap.WriteWRAPSectionInternalPatch(WRAPInternalPatch)
        
        
        # Needed Data to Backpatch
        WRAPSize = WRAPHeaderAndPatch.tell() + WRAPExternalPatch.tell() + WRAPInternalPatch.tell()
        
        IMGSize = MH.tell() + MT.tell() + MI_ST_VS.tell()
        
        IMGPointer = WRAPSize - 24
        
        PHYSSize = 0
        for v, i in zip(VBDatas, IBDatas):
            PHYSSize += v.tell() + i.tell()
            
        PHYSPointer = (WRAPSize + IMGSize) - 32
        
        
        ExternalPatchPointer = WRAPHeaderAndPatch.tell() - 52
        
        InternalPatchCount = mesh_count * 6 + 1
        
        InternalPatchPointer = ( WRAPHeaderAndPatch.tell() + WRAPExternalPatch.tell() ) - 60
        
        GlobalPatchCount = 0
        
        GlobalPatchPointer = WRAPSize - 68
        
        pTargetBackpatchValuesExt = [WRAPSize - (pt + WRAPHeaderAndPatch.tell())  for pt in pointerTargetPOSListExt]"""
        
        

        
        # Vertex Buffer and Index Buffer
        #vertex_buffer_pos = []
        #index_buffer_pos = []
        #for vbd, ibd in zip(VBDatas, IBDatas):          
            
            #vertex_buffer_pos.append(out.tell())
            #out.write(vbd)
            
            #write_alignment_4(out, out.tell())
            
            
            #index_buffer_pos.append(out.tell())
            #out.write(ibd)
            
            #write_alignment_4(out, out.tell())
            
            
        # Backpatching
            
        # Backpatch Model Table
        #model_table.BackpatchModelTable(out, mesh_info_pos)
            
        # Backpatch Mesh Info
        #mesh_info.BackpatchMeshInfo(out, bone_palette_pos, vertex_buffer_pos, index_buffer_pos, schema_table_pos)
        
        # Backpatching Schema Table and Vertex Schema
        #for n, obj in enumerate(mesh_objects):
            # Backpatch Schema Table
            #out.seek(schema_table_pos[n], 0)
            #schema_table.BackpatchSchemaTable(out, all_attributes[n][0][1], first_vertex_schema_pos[n])
            
            # Backpatch Vertex Schema
            #vertex_schema.BackpatchVertexSchema(out, first_vertex_schema_pos[n], all_offset[n], all_type[n], all_usage[n])
        
            
            
        
            
            
           
           
        
            

            
            
            
            
            
            
            
            