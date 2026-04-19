from .Helpers import *

class WRAPSectionHeader():
    def __init__(self):
        # WRAPSection Header
        self.dwMagic = 0
        self.dwPCAPKFilenameHash = 0
        
        self.dwPatchTablePointer = 0
        
        self.dwComponentCount = 0
        self.dwComponentsPointer = 0
        self.dwIMGSize = 0
        self.dwIMGPointer = 0
        self.dwPHYSSize = 0
        self.dwPHYSPointer = 0
        
    def ReadWRAPSectionHeader(self, f):
        self.dwMagic = read_uint(f)
        self.dwPCAPKFilenameHash = read_uint(f)
        self.dwPatchTablePointerPOS = f.tell()
        self.dwPatchTablePointer = read_uint(f)
        self.dwComponentCount = read_uint(f)
        self.dwComponentsPointer = read_uint(f)
        self.dwIMGSize = read_uint(f)
        self.dwIMGPointer = read_uint(f)
        
        if self.dwComponentCount == 2:
            self.dwPHYSSize = read_uint(f)
            self.dwPHYSPointer = read_uint(f)
            
        align_to_16(f, f.tell())
        
        
        
    def WriteWRAPSectionHeader(self, f):
        write_uint(f, self.dwMagic)
        write_uint(f, self.dwPCAPKFilenameHash)
        
        PatchTablePointerStart = f.tell() # For Writing Model
        write_uint(f, self.dwPatchTablePointer)
        
        write_uint(f, self.dwComponentCount)
        write_uint(f, self.dwComponentsPointer)
        
        write_uint(f, self.dwIMGSize)
        
        IMGPointerStart = f.tell() # For Writing Model
        write_uint(f, self.dwIMGPointer)
        
        PHYSPointerStart = None
        
        if self.dwComponentCount == 2:
            write_uint(f, self.dwPHYSSize)
            
            PHYSPointerStart = f.tell() # For Writing Model
            write_uint(f, self.dwPHYSPointer)
        
        write_alignment_16_A1(f, f.tell()) # Alignment
        
        return PatchTablePointerStart, IMGPointerStart, PHYSPointerStart

        
        
        
class WRAPSectionPatchTable():
    def __init__(self):  
        # WRAPSection PatchTable
        self.dwExternalPatchCount = 0
        self.dwExternalPatchPointer = 0
        
        self.dwInternalPatchCount = 0
        self.dwInternalPatchPointer = 0
        
        self.dwGlobalPatchCount = 0
        self.dwGlobalPatchPointer = 0
        
        
    def ReadWRAPSectionPatchTable(self, f):
        self.dwExternalPatchCount = read_uint(f)
        self.dwExternalPatchPointer = read_uint(f)
        
        self.dwInternalPatchCount = read_uint(f)
        self.dwInternalPatchPointer = read_uint(f)
        
        self.dwGlobalPatchCount = read_uint(f)
        self.dwGlobalPatchPointer = read_uint(f)
        
        align_to_16(f, f.tell())
    
    
    def WriteWRAPSectionPatchTable(self, f):
        write_uint(f, self.dwExternalPatchCount)
        ExternalPatchPointerStart = f.tell() # For Writing Model
        write_uint(f, self.dwExternalPatchPointer)

        write_uint(f, self.dwInternalPatchCount)
        InternalPatchPointerStart = f.tell() # For Writing Model
        write_uint(f, self.dwInternalPatchPointer)
        
        write_uint(f, self.dwGlobalPatchCount)
        GlobalPatchPointerStart = f.tell() # For Writing Model
        write_uint(f, self.dwGlobalPatchPointer)

        
        write_alignment_16_A1(f, f.tell()) # Alignment
        
        return ExternalPatchPointerStart, InternalPatchPointerStart, GlobalPatchPointerStart
    
    
    
    
        
class WRAPSectionExternalPatch():
    def __init__(self):
        # WRAPSection ExternalPatch
        self.dwPatchToTypeExternal = 0
        self.dwExternalFilenameHash = b"\x00\x00\x00\x00"
        self.dwExpectedIndexExternal = 0
        self.dwPointerTargetExternal = 0
    
        self.PointerTargetExternalStartList = [] # For Writing Model
        
        self.ExternalFilenameHashList = [] # For Writing Materials FilenameHashes
    
    
    def ReadWRAPSectionExternalPatch(self, f, ExternalPatchCount):
        for external in range(ExternalPatchCount):
                self.dwPatchToTypeExternal = read_uint(f)
                self.dwExternalFilenameHash = f.read(4)
                
                if self.dwPatchToTypeExternal == 5521741:
                    self.ExternalFilenameHashList.append(self.dwExternalFilenameHash)
                
                self.dwExpectedIndexExternal = read_uint(f)
                self.dwPointerTargetExternal = read_uint(f)
                
        
        
        
    
    def WriteWRAPSectionExternalPatch(self, f):
        write_uint(f, self.dwPatchToTypeExternal)
        f.write(self.dwExternalFilenameHash)
        write_uint(f, self.dwExpectedIndexExternal)
        
        
        self.PointerTargetExternalStartList.append(f.tell()) # For Writing Model
        write_uint(f, self.dwPointerTargetExternal)
    
    
    
class WRAPSectionInternalPatch():
    def __init__(self):
        # WRAPSection InternalPatch
        self.dwPointerTargetInternal = 0
        
        self.PointerTargetInternalStartList = [] # For Writing Model
        
    
    def ReadWRAPSectionInternalPatch(self, f, InternalPatchCount):
        for internal in range(InternalPatchCount):
            self.dwPointerTargetInternal = read_uint(f)
            
        align_to_16(f, f.tell())
        
        
    def WriteWRAPSectionInternalPatch(self, f):
        self.PointerTargetInternalStartList.append(f.tell()) # For Writing Model
        write_uint(f, self.dwPointerTargetInternal)