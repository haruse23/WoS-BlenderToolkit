from .ReadModel import *
from .Skeleton import *
from .get_string_lookup import *

from .Morph import *
from .ASKL import *
from .ANIM import *


import bpy
import bmesh
import math
import os
from mathutils import Matrix, Vector, Quaternion

from pathlib import Path

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
        
        if scene.convert_to_triangle_list:
            triangle_faces = convert_triangle_strips_to_triangle_list(indices)
        
        else:
            triangle_faces = [
                (indices[i], indices[i+1], indices[i+2])
                for i in range(0, len(indices), 3)
            ]
            
        if scene.reverse_winding_order:
            triangle_faces = reverse_winding_order_import(triangle_faces)
        
        mesh = bpy.data.meshes.new(f"SMWOS_Mesh_{m}")
        obj = bpy.data.objects.new(f"SMWOS_MeshObject_{m}", mesh)

        mesh.from_pydata(positions, [], triangle_faces)
        mesh.update()
        
        
            
        bm = bmesh.new()
        bm.from_mesh(mesh)
        
        
        
        
                    
        
        # UVs
        for channel, uv_data in Vertex_Buffers[m].TexCoords.items():
            flat_numbers = []

            for face in triangle_faces:
                for v in face:
                    u, vv = uv_data[v][0], uv_data[v][1]

                    if scene.flip_uv_v_avis:
                        vv = 1.0 - vv

                    flat_numbers.append(u)
                    flat_numbers.append(vv)

            uv_layer = mesh.uv_layers.new(name=f"UVMap_{channel}")
            uv_layer.data.foreach_set("uv", flat_numbers)   # all corners at once

        # Colors
        for channel, color_data in Vertex_Buffers[m].Colors.items():
            flat_numbers = []

            for face in triangle_faces:
                for v in face:
                    c = color_data[v]
                    flat_numbers.append(c[0])
                    flat_numbers.append(c[1])
                    flat_numbers.append(c[2])
                    flat_numbers.append(c[3])

            color_layer = mesh.color_attributes.new(f"Col_{channel}", 'BYTE_COLOR', 'CORNER')
            color_layer.data.foreach_set("color", flat_numbers)
           
                
                    
        # Normals
        if Vertex_Buffers[m].Normals:          
            Normals = Vertex_Buffers[m].Normals
                
            attr = mesh.attributes.get("custom_normal")
            if attr is None:
                    attr = mesh.attributes.new("custom_normal", 'FLOAT_VECTOR', 'POINT')
                
            flat_numbers = []
            for normal in Normals:
                flat_numbers.append(normal[0])
                flat_numbers.append(normal[1])
                flat_numbers.append(normal[2])

            attr.data.foreach_set("vector", flat_numbers)    # all vertices at once
        
           
        # Create all vertex groups
        vertex_groups = {}
        for i in Mesh[3]:
            vertex_groups[i] = obj.vertex_groups.new(name=f"bone_{i}")

        # First collect: (bone, weight) -> list of vertices
        weight_batches = {}

        for v_idx, (indices, weights) in enumerate(zip(Vertex_Buffers[m].BlendIndices, Vertex_Buffers[m].BlendWeights)):
            for palette_index, w in zip(indices, weights):
                if w != 0:
                    bone_idx = Mesh[3][palette_index] # Bone index from the palette

                    batch_key = (bone_idx, w)
                    if batch_key not in weight_batches:
                        weight_batches[batch_key] = []

                    weight_batches[batch_key].append(v_idx)

        # Then add each list with ONE call
        for (bone_idx, w), vertex_list in weight_batches.items():
            vertex_groups[bone_idx].add(vertex_list, w, 'REPLACE')

        
        
        
        
        
        mat_name = "0x" + wrap_external.ExternalFilenameHashList[m][::-1].hex().upper()
        mat = bpy.data.materials.new(name=mat_name)
        obj.data.materials.append(mat)
        
        mesh.update()
        
        obj.location = Vector((Mesh[0].ModelOriginX, Mesh[0].ModelOriginY, Mesh[0].ModelOriginZ)) # Mesh[0] is model_header
        # Setting the Mesh Origin for each Mesh Object, instead of adding and baking it into the vertex positions
        
        new_collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
                
        
        

        
        
        




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
            pcapk_hash = f"0x{pcapkFilenameHash:08X}"
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
        
        #bone_y_direction = matrices[i].col[1].to_3d().normalized()
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
    
    
    
    
    
    
    
def ImportMorph(filepath):
    filename_hash, submeshes_vert_count, morphs = ReadMorph(filepath)
  
    morh_name = Path(filepath).name.split(".", 1)[1].rsplit(".", 2)[0] # e.g.: 0xD18DAA59.ch_spiderman_rvbigc000.wrap.morh
    
    mesh_collection = bpy.data.collections.get(morh_name)
    
    mesh_objs = [obj for obj in mesh_collection.objects if obj.type == "MESH"]


    obj = None
    
    aabb_max = Vector((
        float("-inf"),
        float("-inf"),
        float("-inf")
    ))

    for mesh_obj in mesh_objs:
        for vertex in mesh_obj.data.vertices:
            local_vertex = vertex.co

            aabb_max.x = max(aabb_max.x, local_vertex.x)
            aabb_max.y = max(aabb_max.y, local_vertex.y)
            aabb_max.z = max(aabb_max.z, local_vertex.z)
        
        
    for i, morph_deltas in enumerate(morphs):

        obj = bpy.context.active_object
        
        # Create Basis first
        if i == 0: # Only make Basis one time before first Morph
            obj.shape_key_add(name="Basis", from_mix=False)
    
        
        # Create the new shape key
        key = obj.shape_key_add(name=f"{filename_hash}_Morph_{i+1}", from_mix=False)
        key.value = 0.0
            
        # Fill its vertex positions
        vertices = obj.data.vertices
        
        for delta in morph_deltas:
            for vertex_index, values in delta.items():
                position_x = vertices[vertex_index].co.x + values[0] / 1024 * aabb_max[0]
                position_y = vertices[vertex_index].co.y + values[1] / 1024 * aabb_max[1]
                position_z = vertices[vertex_index].co.z + values[2] / 1024 * aabb_max[2]

                key.data[vertex_index].co = Vector((
                    position_x,
                    position_y,
                    position_z
                ))
                
        all_zero = all(
            vertex.co.length == 0
            for vertex in key.data
        )
        
        if all_zero:
            key.name = key.name + "_Empty"

            
            
            
    
    


def ImportASKL(filepath):
    SkeletonName = os.path.splitext(os.path.basename(filepath))[0]
    
    SkeletonName = SkeletonName.rsplit(".")[1]
    
    Bones, positions_bones, rotations_bones, hinges_bones, default_tracks = ReadASKL(filepath)
    
    
    ##############################################
    arm_data = bpy.data.armatures.new(SkeletonName)
    arm_object = bpy.data.objects.new(SkeletonName, arm_data)
    bpy.context.collection.objects.link(arm_object)
    bpy.context.view_layer.objects.active = arm_object
    bpy.ops.object.mode_set(mode='EDIT')
        
    
    for i, bone in enumerate(Bones):
        edit_bone = arm_data.edit_bones.new(bone["Name"])
        
        pos = Vector(bone["Position"])
        
        x, y, z, w = bone["Rotation"]                
        rot = Quaternion((w, x, y, z))  
                                        
        scale = Vector((1, 1, 1))
        
        matrix = Matrix.LocRotScale(pos, rot, scale)
        
        
        edit_bone.head = Vector((0.0, 0.0, 0.0))
        
        edit_bone.tail = Vector((0.0, 0.1, 0.0))
        
        edit_bone.matrix = matrix
        
        
    
    for i, edit_bone in enumerate(arm_data.edit_bones):
        parent_index = Bones[i]["Parent_Index"]
        
        if not parent_index == -1:
            edit_bone.parent = arm_data.edit_bones[parent_index]
            
            
    
    for edit_bone in arm_data.edit_bones:
    
        if edit_bone.parent:
            edit_bone.matrix = edit_bone.parent.matrix @ edit_bone.matrix
        
    
    
    bpy.context.view_layer.update()          
    bpy.ops.object.mode_set(mode='OBJECT')
    
    
def bone_pose_for_frame(tracks, askl_object):
    n = len(askl_object.Bones)

    # start: bind pose from the bone records
    rot = []
    pos = []
    for b in askl_object.Bones:
        x, y, z, w = b["Rotation"]                   # record +0x10
        rot.append(Quaternion((w, -x, -y, -z)))    # Blender convention
        pos.append(Vector(b["Position"][:3]))         # record +0x20
    bind_rot = [q.copy() for q in rot]

    # position tracks → translation
    for i, bone in enumerate(askl_object.positions_list):        # list at askl_object 0x38
        if (0, i) in tracks:
            pos[bone] = Vector(tracks[(0, i)])

    # quaternion tracks → rotation (replaces bind)
    for i, bone in enumerate(askl_object.rotations_list):       # list at askl_object 0x3C
        if (1, i) in tracks:
            x, y, z, w = tracks[(1, i)]
            rot[bone] = Quaternion((w, -x, -y, -z)).normalized()

    # hinge tracks → angle around the bone's axis, on top of bind
    for i, bone in enumerate(askl_object.hinges_list):      # list at askl_object 0x40
        if (2, i) in tracks:
            a = tracks[(2, i)][0]
            ax = askl_object.Bones[bone]["Hinge"]               # record +0x00
            s = math.sin(a / 2)
            hinge = Quaternion((math.cos(a / 2), ax[0]*s, ax[1]*s, ax[2]*s))
            rot[bone] = hinge @ bind_rot[bone]

    return rot, pos
    
    
def rest_local(bone):
    if bone.parent:
        return bone.parent.matrix_local.inverted() @ bone.matrix_local
    return bone.matrix_local.copy()
    
    
def apply_animation(arm_obj, askl_object, anim_name, frames_tracks, frame_time):
    name_to_index = {b["Name"]: i for i, b in enumerate(askl_object.Bones)}

    targets = []
    for pb in arm_obj.pose.bones:
        i = name_to_index.get(pb.name)
        if i is None:
            continue
        pb.rotation_mode = 'QUATERNION'
        targets.append((pb, i, rest_local(pb.bone).inverted()))

    action = bpy.data.actions.new(anim_name)
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = action
    
    
    
    last_q = {}
    scene = bpy.context.scene
    for f, tracks in enumerate(frames_tracks):
        rot, pos = bone_pose_for_frame(tracks, askl_object)
        for pb, i, rest_inv in targets:
            fakeroot = name_to_index.get("fakeroot")

            local = Matrix.LocRotScale(pos[i], rot[i], None)

            if scene.root_motion and fakeroot is not None and pb.parent is None and pb.name != "fakeroot":
                fr = Matrix.LocRotScale(pos[fakeroot], rot[fakeroot], None)
                local = fr @ local                             # carry the body along

            basis = rest_inv @ local
            loc, q, scl = basis.decompose()

            if pb.name in last_q and last_q[pb.name].dot(q) < 0:
                q.negate()                            # no long-way-round spins
            last_q[pb.name] = q

            pb.location = loc
            pb.rotation_quaternion = q
            pb.keyframe_insert("location", frame=f + 1)
            pb.keyframe_insert("rotation_quaternion", frame=f + 1)

    scn = bpy.context.scene
    scn.render.fps = round(1 / frame_time)            # 30
    scn.frame_start = 1
    scn.frame_end = len(frames_tracks)
    
    

def ImportANIM(filepath):
    anim_object, askl_object, frames_tracks = ReadANIM(filepath)

    arm_obj = bpy.context.active_object # User needs to select the armature before import
    
    anim_name = os.path.splitext(os.path.basename(filepath))[0]
    
    anim_name = anim_name.rsplit(".")[1]
    
    apply_animation(arm_obj, askl_object, anim_name, frames_tracks, anim_object.frame_time)
    
    