



def Rename_Vertex_Groups(collection):
    mesh_objects = [obj for obj in collection.objects if obj.type == "MESH"]
    
    armature_obj = None
    for obj in collection.objects:
        if obj.type == "ARMATURE":
            armature_obj = obj
            
    Bones = {}
    for i, bone in enumerate(armature_obj.data.bones):
        Bones[i] = bone.name
    
    #########################################################
    
    for mesh in mesh_objects:
        for vg in mesh.vertex_groups:
            bone_index = int(vg.name.rsplit("_")[1])
            
            bone_name = Bones[bone_index]
            
            vg.name = bone_name