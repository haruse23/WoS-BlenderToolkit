from .Helpers import *
from .Wrap import *

class MorphHeader:
    def Read(self, f):
        self.FilenamePointer = read_uint(f)
        self.FilenameHash = read_uint(f)
        self.MorphTargetCount = read_uint(f)
        
        
        self.RelativePointer = read_uint(f)
        
        
        
        
    def Write(self, out):
        write_uint(out, self.FilenamePointer)
        write_uint(out, self.FilenameHash)
        write_uint(out, self.MorphTargetCount)
        
        self.PointerPosition = out.tell()
        write_uint(out, 4)
        
        
        
        
        

class MorphOffsetTable:
    def Read(self, f):
        self.unk = read_uint(f)
        self.submesh_count = read_uint(f)
        self.PointerPosition = f.tell()
        self.MorphDataPointer = read_uint(f) # Relative
        
        
        
    def Write(self, out):
        write_uint(out, self.unk)
        write_uint(out, self.submesh_count)
        
        self.PointerPosition = out.tell()
        write_uint(out, self.MorphDataPointer)
        
        
        
        
        
        
class MorphData:
    def Read(self, f, vertex_count):

        total_n_delta = 0
        total_n_skip = 0
        
        self.Deltas = []
        vertex_index = 0
            
        while True:
            n_delta = read_ushort(f)
            n_skip = read_ushort(f)

            for i in range(n_delta):
                deltaX = read_vertex_position_short(f)
                deltaY = read_vertex_position_short(f)
                deltaZ = read_vertex_position_short(f)
                deltaW = read_vertex_position_short(f)

                self.Deltas.append(
                    {
                        vertex_index: (deltaX, deltaY, deltaZ, deltaW)
                    }
                )

                vertex_index += 1
            
            vertex_index += n_skip
            
            total_n_delta += n_delta # Total number of deltas read
            total_n_skip += n_skip # Total number of vertices skipped
            
            # Must sum to (vertex_count)
            
            if total_n_delta + total_n_skip == vertex_count:
                break
                
                
                
            
        
        
        
    def Write(self, out, vertex_count):
        i = 0

        while i < vertex_count:
            # Count consecutive vertices with nonzero deltas
            start = i
            n_delta = 0

            while i < vertex_count and self.Deltas[i] != (0, 0, 0):
                n_delta += 1
                i += 1

            # Count consecutive zero-delta vertices AFTER the run
            n_skip = 0

            while i < vertex_count and self.Deltas[i] == (0, 0, 0):
                n_skip += 1
                i += 1

            write_ushort(out, n_delta)
            write_ushort(out, n_skip)

            # Write the deltas in this run
            for j in range(start, start + n_delta):
                vertex_delta = self.Deltas[j]

                write_short(out, vertex_delta[0])  # X
                write_short(out, vertex_delta[1])  # Y
                write_short(out, vertex_delta[2])  # Z
                write_short(out, 0)                 # W
            
            
        
        
        
        
        
def ReadMorph(filepath):
    with open(filepath, "rb") as f:
        wrap = WRAPSectionHeader()
        wrap.ReadWRAPSectionHeader(f)
        
        wrap_patch = WRAPSectionPatchTable()
        wrap_patch.ReadWRAPSectionPatchTable(f)
        
        wrap_external = WRAPSectionExternalPatch()
        wrap_external.ReadWRAPSectionExternalPatch(f, wrap_patch.dwExternalPatchCount)
        
        wrap_internal = WRAPSectionInternalPatch()
        wrap_internal.ReadWRAPSectionInternalPatch(f, wrap_patch.dwInternalPatchCount)
        
        
        morph_header = MorphHeader()
        morph_header.Read(f)
        
        morph_offsets = []
        morph_offsets_submesh_count = []
        for i in range (morph_header.MorphTargetCount):
            morph_offset_table = MorphOffsetTable()
            morph_offset_table.Read(f)
            
            morph_offsets.append(morph_offset_table.PointerPosition + morph_offset_table.MorphDataPointer)
            morph_offsets_submesh_count.append(morph_offset_table.submesh_count)
        
        
        
        morphs = []
        submeshes_vertex_count = []
        for i, morph_offset in enumerate(morph_offsets):   
            f.seek(morph_offset, 0)
            
            found_vertex_count = 0
            for i in range(morph_offsets_submesh_count[i]): # 12 bytes per mesh in every morph target data block
                vertex_count = read_uint(f)
                _one_ = read_uint(f)
                relative_pointer = read_uint(f)
                
                if vertex_count:
                    found_vertex_count = vertex_count
                
                  
            DeltaStreamPointer = read_uint64(f)
            
            f.seek(DeltaStreamPointer, 1)
            
            if found_vertex_count == 0:
                continue
                
            morph_data = MorphData()
            morph_data.Read(f, found_vertex_count)

            morphs.append(morph_data.Deltas)
            
            submeshes_vertex_count.append(found_vertex_count)
            
            
            
            
    return morph_header.FilenameHash, submeshes_vertex_count, morphs

        
        
        
        
        
        