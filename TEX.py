import struct
from .Hash import *

from .Helpers import *

class TEX:
    def __init__(self):
        self.dwUnused1 = b''
        self.dwFilenamePointer = 0
        self.dwFilenameHash = 0
        self.dwUnused2 = b''
        self.dwWidth = 0
        self.dwHeight = 0
        self.dwDepth = 0
        self.dwMipMapCount = 0
        self.dwFourCC = b''
        self.dwUnused3 = b''
        self.dataTEX = b''
        
        
    def ReadTEX(self, f):
        self.dwUnused1 = f.read(2 * 4)
        self.dwFilenamePointer = read_uint(f)
        self.dwFilenameHash = read_uint(f)
        self.dwUnused2 = f.read(2 * 4)
        self.dwWidth = read_uint(f)
        self.dwHeight = read_uint(f)
        self.dwDepth = read_uint(f)
        self.dwMipMapCount = read_uint(f)
        self.dwFourCC = f.read(4)
        self.dwUnused3 = f.read(6 * 4)
        f.seek(4, 1) # PHYS
        self.dataTEX = f.read()
        
   
        
    
    def ConvertToTEX(self, DDS, Filename):
        self.dwUnused1 = b'\x00' * 2 * 4
        self.dwFilenamePointer = 0
        self.dwFilenameHash = Hash(Filename)
        self.dwUnused2 = b'\x00' * 2 * 4
        self.dwWidth = DDS.dwWidth
        self.dwHeight = DDS.dwHeight
        self.dwDepth = DDS.dwDepth
        self.dwMipMapCount = DDS.dwMipMapCount
        
        if DDS.dwFourCC == b'DXT1' or DDS.dwFourCC == b'DXT3' or DDS.dwFourCC == b'DXT5': # Compressed DXT
            self.dwFourCC = DDS.dwFourCC
            
        elif DDS.dwFourCC == b'\x00' * 4:
            if DDS.dwFlagsPF & 0x40 and DDS.dwFlagsPF & 0x1: # Uncompressed A8R8G8B8
                self.dwFourCC = b'\x15\x00\x00\x00'
                
            elif DDS.dwFlagsPF & 0x40: # Uncompressed X8R8G8B8
                self.dwFourCC = b'\x16\x00\x00\x00'
                
            elif DDS.dwFlagsPF & 0x20000: # Uncompressed L8
                self.dwFourCC = b'\x32\x00\x00\x00'
            
        self.dwUnused3 = b'\x00' * 6 * 4
        self.dataTEX = DDS.dataDDS
     
    
    def WriteTEX(self, f):
        f.write(self.dwUnused1)
        write_uint(f, self.dwFilenamePointer)
        write_uint(f, self.dwFilenameHash)
        f.write(self.dwUnused2)
        write_uint(f, self.dwWidth)
        write_uint(f, self.dwHeight)
        write_uint(f, self.dwDepth)
        write_uint(f, self.dwMipMapCount)
        f.write(self.dwFourCC)
        f.write(self.dwUnused3)
        f.write(b"PHYS")
        f.write(self.dataTEX)
        
        
        
        
    
        
        
        
    