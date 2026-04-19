from .Helpers import *
from .Wrap import *

class SkeletonHeader():
    def __init__(self):
        self.FilenamePointer = 0
        self.FilenameHash = 0
        self.BoneCount = 0
        
        self.SkeletonDataStartPointerPOS = 0
        self.SkeletonDataStartPointer = 0


    def ReadSkeletonHeader(self, f):
        self.FilenamePointer = read_uint(f)
        self.FilenameHash = read_uint(f)
        self.BoneCount = read_uint(f)
        
        self.SkeletonDataStartPointerPOS = f.tell()
        self.SkeletonDataStartPointer = read_uint(f)
        
        
        
    def WriteSkeletonHeader(self, f):
        write_uint(f, self.FilenamePointer)
        write_uint(f, self.FilenameHash)
        write_uint(f, self.BoneCount)
        
        write_uint(f, self.SkeletonDataStartPointer)
        
        
        
        
        
        
        
class SkeletonData():
    def __init__(self):
        self.UnknownData = b'\x00' * 64
        self.InverseBindPoseMatrix = b'\x00' * 64
        
        self.BonenamePointerStartList = []
        self.BonenamePointer = 0
        self.BonenameHash = 0
        self.BoneParentIndex = 0
        self.UnknownInt = 0
        
        self.rotX1 = 0
        self.rotX2 = 0
        self.rotX3 = 0
        self.Unknown1 = 0

        self.rotY1 = 0
        self.rotY2 = 0
        self.rotY3 = 0
        self.Unknown2 = 0
        
        self.rotZ1 = 0
        self.rotZ2 = 0
        self.rotZ3 = 0
        self.Unknown3 = 0

        self.pos_x = 0
        self.pos_y = 0
        self.pos_z = 0
        self.Unknown4 = 0
        
        
    def ReadSkeletonData(self, f):
        self.UnknownData = f.read(64)
        
        self.InverseBindPoseMatrix = f.read(64)
        
        self.rotX1 = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x0)[0]
        self.rotX2 = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x4)[0]
        self.rotX3 = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x8)[0]
        self.Unknown1 = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0xC)[0]

        self.rotY1 = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x10)[0]
        self.rotY2 = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x14)[0]
        self.rotY3 = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x18)[0]
        self.Unknown2 = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x1C)[0]

        self.rotZ1 = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x20)[0]
        self.rotZ2 = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x24)[0]
        self.rotZ3 = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x28)[0]
        self.Unknown3 = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x2C)[0]

        self.pos_x = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x30)[0]
        self.pos_y = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x34)[0]
        self.pos_z = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x38)[0]
        self.Unknown4 = struct.unpack_from("<f", self.InverseBindPoseMatrix, 0x3C)[0]
        
        
        self.BonenamePointer = read_uint(f)
        self.BonenameHash = read_uint(f)
        self.BoneParentIndex = read_uint(f)
        self.UnknownInt = read_uint(f)
        
    
    def WriteSkeletonData(self, f):
        f.write(self.UnknownData)

        f.write(self.InverseBindPoseMatrix)
        
        self.BonenamePointerStartList.append(f.tell())
        write_uint(f, self.BonenamePointer)
        write_uint(f, self.BonenameHash)
        
        if self.BoneParentIndex != -1:
            write_uint(f, self.BoneParentIndex)
        else:
            f.write(b"\xFF" * 4)
        
        write_uint(f, self.UnknownInt)
        
        




def ReadSkeleton(filepath):
    with open(filepath, "rb") as f:
        Bones = []
        
        wrap_header = WRAPSectionHeader()
        wrap_header.ReadWRAPSectionHeader(f)
        
        
        wrap_patchtable = WRAPSectionPatchTable()
        wrap_patchtable.ReadWRAPSectionPatchTable(f)

  
        wrap_external = WRAPSectionExternalPatch()
        wrap_external.ReadWRAPSectionExternalPatch(f, wrap_patchtable.dwExternalPatchCount)
        
        
        wrap_internal = WRAPSectionInternalPatch()
        wrap_internal.ReadWRAPSectionInternalPatch(f, wrap_patchtable.dwInternalPatchCount)
        
        
        skeleton_header = SkeletonHeader()
        skeleton_header.ReadSkeletonHeader(f)
        
        for s in range(skeleton_header.BoneCount):
            skeleton_data = SkeletonData()
            skeleton_data.ReadSkeletonData(f)
            
            Bones.append(skeleton_data)
            
        
        
        
        
        
        





    return Bones, wrap_header.dwPCAPKFilenameHash




    
    



















