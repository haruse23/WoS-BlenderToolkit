from .Helpers import *
from .Wrap import *

from .get_string_lookup import lookup_pcapk_string_table

class ASKL:
    def Read(self, f):
        self.FilenamePointer = read_uint(f)
        self.FilenameHash = read_uint(f)
        
        self.table_pointer = f.tell() + read_uint(f)
        self.pose_layout_pointer = f.tell() + read_uint(f)
        
        f.seek(self.table_pointer) 
        f.seek(8, 1)
        
        self.bone_count = read_uint(f)
        self.bones_default_poses_pointer = f.tell() + read_uint(f)
        
        f.seek(8, 1)
        
        self.positions_pointer = f.tell() + read_uint(f)
        self.rotations_pointer = f.tell() + read_uint(f)
        self.hinges_pointer = f.tell() + read_uint(f)
        
        f.seek(self.pose_layout_pointer)
        f.seek(4, 1)
        
        self.default_tracks_pointer = f.tell() + read_uint(f)
        
        f.seek(84, 1)
        
        self.default_tracks_bytesize = read_uint(f)
        
        precision_pointers = []
        for i in range(11):
            precision_pointer = f.tell() + read_uint(f)
            
            precision_pointers.append(precision_pointer)
            
        
        self.counts_per_tracktype = []
        for i in range(11):
            count_per_track = read_ushort(f)
            
            self.counts_per_tracktype.append(count_per_track)
            
        
        self.track_offsets = [read_ushort(f) for _ in range(11)] # In default-tracks buffer
        self.track_slots   = [read_ushort(f) for _ in range(11)]
            
        
        # Read Positions List, Bones referenced by the position track
        f.seek(self.positions_pointer)
        
        self.positions_list = []
        for i in range(self.counts_per_tracktype[0]): # First one
            bone = read_ushort(f)
            
            self.positions_list.append(bone)
            
        
        # Read Rotations List, Bones referenced by the rotation track
        f.seek(self.rotations_pointer)
        
        self.rotations_list = []
        for i in range(self.counts_per_tracktype[1]): # Second one
            bone = read_ushort(f)
            
            self.rotations_list.append(bone)
            
        # Read Hinges List, Bones referenced by the hinge track
        f.seek(self.hinges_pointer)
        
        self.hinges_list = []
        for i in range(self.counts_per_tracktype[2]): # Third one
            bone = read_ushort(f)
            
            self.hinges_list.append(bone)
            

        # Read default_tracks buffer
        f.seek(self.default_tracks_pointer)
        
        floats_per_track = [4, 4, 1, 4, 8, 1, 6, 1, 4, 4, 9] # position, rotation, hinge etc
 
        self.default_tracks = []
        for i in range(11):
            
            track = []
            for j in range(self.counts_per_tracktype[i]):
            
                float_datas = []
                for k in range(floats_per_track[i]):
                    float_data = read_float(f)
                    
                    float_datas.append(float_data)
                    
                    
            track.append(float_datas)
                    
        
            align_to_16(f, f.tell())
            
        self.default_tracks.append(track)    
            
            
        self.precisions = []
        for i, precision_pointer in enumerate(precision_pointers):
            precisions_per_type = []
            
            if precision_pointer != 0:
                f.seek(precision_pointer)
                
                
                for m in range(self.counts_per_tracktype[i]):
                    precision = read_float(f)
                
                    precisions_per_type.append(precision)
                    
            self.precisions.append(precisions_per_type)
            
            
        
            
        # Parse default bone poses
        f.seek(self.bones_default_poses_pointer)
        
        self.Bones = []
        for i in range(self.bone_count):
        
            hinge_floats = []
            for h in range(4):
                r_float = read_float(f)
                hinge_floats.append(r_float)
                
            
            rotation_floats = []
            for r in range(4):
                r_float = read_float(f)
                rotation_floats.append(-r_float) # Negate/conjugate for Blender
                
            
            position_floats = []
            for p in range(4):
                r_float = read_float(f)
                
                if p == 3: # Ignore 4th, read but don't append
                    continue
                    
                position_floats.append(r_float)
                
            
            
            parent_index = read_int(f)
            
            bonename_pointer = read_uint(f)
            bone_hash = read_uint(f)
            
            f.seek(4, 1) # Unknown
            
            self.Bones.append( {"Hinge": hinge_floats, "Rotation": rotation_floats, "Position": position_floats, "Parent_Index": parent_index, "Name": bonename_pointer, "Hash": bone_hash} )
            
                
        
        

def ReadASKL(filepath):
    with open(filepath, "rb") as f:
        wrap = WRAPSectionHeader()
        wrap.ReadWRAPSectionHeader(f)
        
        wrap_patch = WRAPSectionPatchTable()
        wrap_patch.ReadWRAPSectionPatchTable(f)
        
        wrap_external = WRAPSectionExternalPatch()
        wrap_external.ReadWRAPSectionExternalPatch(f, wrap_patch.dwExternalPatchCount)
        
        wrap_internal = WRAPSectionInternalPatch()
        wrap_internal.ReadWRAPSectionInternalPatch(f, wrap_patch.dwInternalPatchCount)
        
        
        askl_object = ASKL()
        askl_object.Read(f)
        
        
        for bone in askl_object.Bones:
            bone["Name"] = lookup_pcapk_string_table(f"0x{wrap.dwPCAPKFilenameHash:08X}", bone["Name"]) # Convert the pcapk filename hash to 8 hexadecimal digits uppercase and append "0x" in the beginning
            
            
        
        
    return askl_object.Bones, askl_object.positions_list, askl_object.rotations_list, askl_object.hinges_list, askl_object.default_tracks
            
            