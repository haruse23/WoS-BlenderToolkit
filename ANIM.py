from .Helpers import *
from .Wrap import *
from .ASKL import *

from .get_string_lookup import lookup_pcapk_string_table

from .bitreader import *

class ANIM:
    def Read(self, f):
        self.FilenamePointer = read_uint(f)
        self.FilenameHash = read_uint(f)
        
        f.seek(4, 1)
        
        self.ASKL_filename_p = read_uint(f)
        self.ASKL_filename_hash = read_uint(f)
        
        f.seek(4, 1)
        self.unk_value = read_uint(f) # Same as in the ASKL
        
        f.seek(4, 1)
        
        self.loop_flag = read_uint(f)
        self.duration = read_float(f)
        self.frame_time = read_float(f)
        
        f.seek(4, 1)
        self.frame_count = read_uint(f)
        
        self.tail_p = f.tell() + read_int(f)
        
        self.total_channel_count = read_uint(f)
        
        f.seek(8, 1)
        self.stream_a_p = f.tell() + read_int(f)
        
        self.stream_b_p = f.tell() + read_int(f)
        
        
        self.stream_b_substreams_p = []
        for i in range(8):
            substream_p = read_uint(f)
            
            self.stream_b_substreams_p.append(substream_p)
        
        
        self.bit_offset_in_streamA = read_uint(f) # For stream A, frames 2+
        
        self.extra_table_p = f.tell() + read_int(f)
        
        self.extra_channel_count = read_ushort(f)
        
        f.seek(2, 1) # CD CD
        
        
        mask_data = f.read(104)
        
        bitreader_mask = BitReader(mask_data)
        
        self.is_stored = []
        for i in range(416):
            # Stored mask
            bit = bitreader_mask.read_bit()
            
            self.is_stored.append(bit)
            
            
        self.is_reset = []
        for i in range(416):
            # Reset to default mask
            bit = bitreader_mask.read_bit()
            
            self.is_reset.append(bit)
            
            
        
        stream_a_size = self.stream_b_p - self.stream_a_p
        
        stream_a_data = f.read(stream_a_size)
        
        bitreader_A = BitReader(stream_a_data)
 
        self.frames = []
        
        G = (self.total_channel_count - self.extra_channel_count) // 8
        
        for i in range(2): # Frame 0 or 1
            
            channels_A = []
            
            for j in range(self.total_channel_count):
                bitcode = bitreader_A.read_bits(6)
                
                number = self.ParseStreamA(bitreader_A, bitcode)
                
                if i == 1: # Frame 1, add it to frame 0
                    number += self.frames[0][j]
                
                channels_A.append(number)
                
            self.frames.append(channels_A)
                    
            
        
        rest_bitcodes = []
        for j in range(self.total_channel_count): # First comes the bitcodes for all channels once [0, N], residuals for corrections
            bitcode = bitreader_A.read_bits(6)
            
            rest_bitcodes.append(bitcode)
        
        
        
        stream_b_size =  self.extra_table_p - self.stream_b_p
        
        stream_b_data = f.read(stream_b_size)
        
        rest_frames_numbers = [[0] * self.total_channel_count for _ in range(self.frame_count - 2)]

        # The [0, N] Channels in Stream B
        # B numbers: piece by piece
        for j in range(8):
            bitreader_B = BitReader(stream_b_data)
            bitreader_B.seek(self.stream_b_substreams_p[j])
            
            for i in range(self.frame_count - 2):
                for g in range(G):
                    c = 8 * g + j
                    rest_frames_numbers[i][c] = self.ParseStreamB(bitreader_B, rest_bitcodes[c])
                    
                    
        # A numbers + prediction, frame by frame
        for i in range(self.frame_count - 2): # Rest of frames, contains only Channels [8G, N]
            # Then the [8G, N] Channels in Stream A
            for k in range(8 * G, self.total_channel_count, 1):
                number = self.ParseStreamA(bitreader_A, rest_bitcodes[k])
                

                rest_frames_numbers[i][k] = number
        
        
        
        
            prev = self.frames[-2]
            cur  = self.frames[-1]
            new = [rest_frames_numbers[i][c] + 2 * cur[c] - prev[c] for c in range(self.total_channel_count)]
            
            
            self.frames.append(new)

            
        
        
        # Extra Channels
        # read the table (E × u16) once
        f.seek(self.extra_table_p)
        self.extra_table = [read_ushort(f) for _ in range(self.extra_channel_count)]

        

        self.frames = [self.Reorder(fr) for fr in self.frames]    
       
            
    def ParseStreamA(self, bitreader, bitcode):
        W = [0,1,2,3,4,5,6,7,8,9,10,11,12,15,20,30] # Width list
                
        if bitcode < 4:
            return 0
            
        elif bitcode >= 4:
            exist_flag = bitreader.read_bit()
            
            if exist_flag: # 1
                wide_flag = bitreader.read_bit()
                
                k = (bitcode & 3) + 2
                index_W = (bitcode >> 2)
                
                if wide_flag: # 1
                    value = bitreader.read_bits(W[index_W] + 1)
                    
                    magnitude = (1 << k) + 1 + (value >> 1)
                    
                    
                
                else: # 0
                    value = bitreader.read_bits(k + 1)
                    
                    magnitude = 0 + 1 + (value >> 1)
                    
                    
                    
                
                number = -magnitude if (value & 1) else magnitude
                
                
            else: # 0
                return 0
                
                
        
        return number
        
        
        
    def ParseStreamB(self, bitreader, bitcode):
        W = [0,1,2,3,4,5,6,7,8,9,10,11,12,15,20,30] # Width list
               
        if bitcode == 0:
            return 0
            
        elif bitcode > 0:
            exist_flag = bitreader.read_bit()
            
            if exist_flag: # 1
                wide_flag = bitreader.read_bit()
                
                k = (bitcode & 3) + 2
                index_W = (bitcode >> 2)
                
                if wide_flag: # 1
                    value = bitreader.read_bits(W[index_W] + 1)
                    
                    magnitude = (1 << k) + 1 + (value >> 1)
                    
                    
                
                else: # 0
                    value = bitreader.read_bits(k + 1)
                    
                    magnitude = 0 + 1 + (value >> 1)
                    
                    
                    
                
                number = -magnitude if (value & 1) else magnitude
                
                
            else: # 0
                return 0
                
                
        
        return number
        
        
        
        
    def Reorder(self, fr):
        N2 = self.total_channel_count - self.extra_channel_count
        G = N2 // 8

        # step 1: undo the groups of 8 (regular channels only)
        out = [fr[8*g + j] for j in range(8) for g in range(G)] + fr[8*G:N2]

        # step 2: put the extras back where they belong
        for s in range(self.extra_channel_count):
            out.insert(self.extra_table[s] + s, fr[N2 + s])

        return out
        
        
    def frame_to_tracks(self, frame, askl_object):
        CHANNELS = [3, 4, 1, 3, 0, 1, 6, 1, 3, 4, 9]
        
        tracks = {}            # (type, track) -> list of floats
        k = 0                  # position in the frame list
        for t in range(11):
            for i in range(askl_object.counts_per_tracktype[t]):
                bit = askl_object.track_slots[t] + i
                
                in_list = self.is_stored[bit] and not self.is_reset[bit]
                
                if not in_list:
                    continue                       # no ints for this track
                    
                n = CHANNELS[t]
                ints = frame[k : k + n]
                k += n
                p = askl_object.precisions[t][i] if askl_object.precisions[t] else 1.0
                
                tracks[(t, i)] = [x * p for x in ints]
                
        assert k == len(frame)                     # must use all N
        return tracks
        
        
        
        
        




import os

def ReadANIM(filepath):
    with open(filepath, "rb") as f:
        wrap = WRAPSectionHeader()
        wrap.ReadWRAPSectionHeader(f)
        
        wrap_patch = WRAPSectionPatchTable()
        wrap_patch.ReadWRAPSectionPatchTable(f)
        
        wrap_external = WRAPSectionExternalPatch()
        wrap_external.ReadWRAPSectionExternalPatch(f, wrap_patch.dwExternalPatchCount)
        
        wrap_internal = WRAPSectionInternalPatch()
        wrap_internal.ReadWRAPSectionInternalPatch(f, wrap_patch.dwInternalPatchCount)
        
        
        anim_object = ANIM()
        anim_object.Read(f)
        
        askl_name = lookup_pcapk_string_table(f"0x{wrap.dwPCAPKFilenameHash:08X}", anim_object.ASKL_filename_p) # Convert the pcapk filename hash to 8 hexadecimal digits uppercase and append "0x" in the beginning
        folder = os.path.dirname(filepath)
        askl_filename = os.path.join(folder, f"0x{anim_object.ASKL_filename_hash:08X}.{askl_name}.wrap.askl")
              
        if not os.path.isfile(askl_filename):
            raise Exception(f"You need this file to import this animation: {os.path.basename(askl_filename)}")

        else:
            with open(askl_filename, "rb") as f2:
                askl_wrap = WRAPSectionHeader()
                askl_wrap.ReadWRAPSectionHeader(f2)
                
                askl_wrap_patch = WRAPSectionPatchTable()
                askl_wrap_patch.ReadWRAPSectionPatchTable(f2)
                
                askl_wrap_external = WRAPSectionExternalPatch()
                askl_wrap_external.ReadWRAPSectionExternalPatch(f2, askl_wrap_patch.dwExternalPatchCount)
                
                askl_wrap_internal = WRAPSectionInternalPatch()
                askl_wrap_internal.ReadWRAPSectionInternalPatch(f2, askl_wrap_patch.dwInternalPatchCount)
                
                
                askl_object = ASKL()
                askl_object.Read(f2)
                
                for bone in askl_object.Bones:
                    bone["Name"] = lookup_pcapk_string_table(f"0x{askl_wrap.dwPCAPKFilenameHash:08X}", bone["Name"])
                
            frames_tracks = [anim_object.frame_to_tracks(frame, askl_object) for frame in anim_object.frames]
            
        
        
        
    
    return anim_object, askl_object, frames_tracks