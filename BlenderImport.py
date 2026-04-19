from .ReadModel import *
from .Skeleton import *
from .get_string_lookup import *

import bpy
import bmesh
import math
import os
from mathutils import Matrix, Vector, Quaternion

def ImportModel(filepath):
    ModelName = os.path.splitext(os.path.basename(filepath))[0]
    
    ModelName = ModelName.rsplit(".")[1]
    
    Model, Vertex_Buffers, Index_Buffers, wrap_external = ReadModel(filepath)
    
    collection_name = ModelName
    new_collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(new_collection)
    scene = bpy.context.scene
    
    for m, Mesh in enumerate(Model):
        positions = Vertex_Buffers[m].Positions
        
        indices = Index_Buffers[m].Indices
        
        if scene.convert_triangle_strips:
            triangle_faces = convert_triangle_strips_to_triangle_list(indices)
        
        else:
            triangle_faces = [
                (indices[i], indices[i+1], indices[i+2])
                for i in range(0, len(indices), 3)
            ]
        
        mesh = bpy.data.meshes.new(f"SMWOS_Mesh_{m}")
        obj = bpy.data.objects.new(f"SMWOS_MeshObject_{m}", mesh)

        mesh.from_pydata(positions, [], triangle_faces)
        mesh.update()
        
        
            
        bm = bmesh.new()
        bm.from_mesh(mesh)
        
        
        
        
                    
        
        # UVs
        if Vertex_Buffers[m].TexCoords:
            for key in Vertex_Buffers[m].TexCoords:
                uv_layer = bm.loops.layers.uv.new("UVMap_" + str(key))
                
                uv_data = Vertex_Buffers[m].TexCoords[key]
                for face in bm.faces:
                    for loop in face.loops:
                        vert_index = loop.vert.index
                        u, v = uv_data[vert_index]
                        loop[uv_layer].uv = (u, v)
                    
            

        print(len(Vertex_Buffers[m].Colors))
        if Vertex_Buffers[m].Colors:
            for key in Vertex_Buffers[m].Colors:
                color_layer = bm.loops.layers.color.new("Col_" + str(key))
                
                color_data = Vertex_Buffers[m].Colors[key]
                for face in bm.faces:
                    for loop in face.loops:
                        vertex_index = loop.vert.index
                        loop[color_layer] = color_data[vertex_index]
                        
                        
        if scene.flip_face_normals:
            flip_face_normals_collection(bm)
            
        if scene.flip_uv:
            flip_uv_collection(bm)
            
        bm.to_mesh(mesh)
        bm.free()
        
        # Normals
        if Vertex_Buffers[m].Normals:
            print(f"Normals Length: {len(Vertex_Buffers[m].Normals)}")
            
            Normals = []
            
            if scene.flip_vertex_normals:
                for Normal in Vertex_Buffers[m].Normals:
                    Normals.append((-Normal[0], -Normal[1], -Normal[2]))
                    
            else:
                Normals = Vertex_Buffers[m].Normals
                
                    
            
            mesh.normals_split_custom_set_from_vertices(Normals)
            mesh.update()
           
        # Create all vertex groups
        for i in Mesh[2]:
            obj.vertex_groups.new(name=f"bone_{i}")

        
        
        for v_idx, (indices, weights) in enumerate(zip(Vertex_Buffers[m].BlendIndices, Vertex_Buffers[m].BlendWeights)):
            for palette_index, w in zip(indices, weights):
                    bone_idx = Mesh[2][palette_index] # Bone index from the palette
                    
                    if w != 0:
                        obj.vertex_groups[f"bone_{bone_idx}"].add([v_idx], w, 'REPLACE')

        
        
        
        mat_name = "0x" + wrap_external.ExternalFilenameHashList[m][::-1].hex().upper()
        mat = bpy.data.materials.new(name=mat_name)
        obj.data.materials.append(mat)
        
        
        new_collection.objects.link(obj)
        
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
                
        #bpy.ops.object.shade_auto_smooth(use_auto_smooth=True, angle=math.radians(180))
        

        
        
        




def ImportSkeleton(filepath):
    SkeletonName = os.path.splitext(os.path.basename(filepath))[0]
    
    SkeletonName = SkeletonName.rsplit(".")[1]
    
    Bones, pcapkFilenameHash = ReadSkeleton(filepath)
    
    
    ##############################################
    arm_data = bpy.data.armatures.new(SkeletonName)
    arm_object = bpy.data.objects.new(SkeletonName, arm_data)
    bpy.context.collection.objects.link(arm_object)
    bpy.context.view_layer.objects.active = arm_object
    bpy.ops.object.mode_set(mode='EDIT')
        
    matrices = []
    
    pos = []
    rot = []
    scale = []
    
    bones = []
    bone_names = []
    
    rot_quat = []
    
    pos = []
    
    parent_indices = []
    
    for i, bone in enumerate(Bones):
        M = Matrix((
            (bone.rotX1, bone.rotX2, bone.rotX3, 0.0),
            (bone.rotY1, bone.rotY2, bone.rotY3, 0.0),
            (bone.rotZ1, bone.rotZ2, bone.rotZ3, 0.0),
            (bone.pos_x, bone.pos_y, bone.pos_z, 1.0)
        ))
        
        
            
        
        # Invert to get bind pose and transpose to match blender's column-major order
        M.invert()
        
        M.transpose()
        matrices.append(M)
        
        rot_matrix = Matrix((
            (M[0][0], M[0][1], M[0][2]),
            (M[1][0], M[1][1], M[1][2]),
            (M[2][0], M[2][1], M[2][2]),
        ))
        
        rot_quat.append(rot_matrix.to_quaternion())
        
        pos.append(Vector((M[0][3], M[1][3], M[2][3])))
        

        parent_index = bone.BoneParentIndex
        parent_indices.append(parent_index)
        
        if pcapkFilenameHash and bone.BonenamePointer:
            pcapk_hash = f"0x{pcapkFilenameHash:X}"
            bone_name = lookup_pcapk_string_table(pcapk_hash, bone.BonenamePointer)
        else:
            bone_name = f"bone_{i}"
        
        
        
            
        edit_bone = arm_data.edit_bones.new(bone_name)
        
        bones.append(edit_bone)
        bone_names.append(bone_name)
        
        
    for i, bone in enumerate(bones):
        edit_bone = bones[i]

        parent_index = parent_indices[i]
        
        if 0 <= parent_index < len(Bones):
            edit_bone.parent = bones[parent_index]
        
        edit_bone.head = Vector((0.0, 0.0, 0.0))
        edit_bone.tail = Vector((0.0, 0.1, 0.0))
        
        edit_bone.matrix = matrices[i]

   
    
    """for i, bone in enumerate(bones):
        edit_bone = bones[i]
        if edit_bone.children:
            # Point tail to average of children heads
            avg = sum((child.head for child in edit_bone.children), edit_bone.head) / (len(edit_bone.children) + 1)
            edit_bone.tail = avg
        else:
            # No children → give it a small default direction
            edit_bone.tail = edit_bone.head + Vector((0, 0.1, 0))"""
            
    bpy.context.view_layer.update()          
    bpy.ops.object.mode_set(mode='OBJECT')
    
    