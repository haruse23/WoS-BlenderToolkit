import os
from .Hash import *
from .Wrap import *

from .DDS import *
from .TEX import *

def Convert(Filepath, DDS, TEX):
    File = os.path.basename(Filepath)
    Filename = os.path.splitext(File)[0]
    DirectoryPath = os.path.dirname(Filepath)
    Extension = Filepath.lower().split('.')[-1].lower()
    
    Path = os.path.join(DirectoryPath, Filename)
    
    
    
    if Extension == 'dds':
        PathOutputTEX = os.path.join(DirectoryPath, Filename + ".wrap.tex")
        with open(Filepath, 'rb') as f:
            dds = DDS()
            dds.ReadDDSHeader(f) # Read DDS
            dds.ReadDDSData(f)

            
        with open(PathOutputTEX, 'wb') as f:
            ############################################################
            # Writing Wrap Section (Header)
            wrap_header_start = f.tell()
            
            wrap_header = WRAPSectionHeader()
            
            wrap_header.dwMagic = 1346458199 # WRAP bytes in decimal, interpreted as 4-byte unsigned int
            
            wrap_header.dwPatchTablePointer = 0x28
            
            wrap_header.dwComponentCount = 2
            wrap_header.dwComponentsPointer = 0x4
            
            wrap_header.dwIMGSize = 0x44
            wrap_header.dwIMGPointer = 0x48
            
            wrap_header.dwPHYSSize = len(dds.dataDDS)
            wrap_header.dwPHYSPointer = 0x88
            
            
            PatchTablePointerStart, IMGPointerStart, PHYSPointerStart = wrap_header.WriteWRAPSectionHeader(f)


            # Writing WRAP Section (PatchTable)
            wrap_patchtable_start = f.tell()
            
            wrap_patchtable = WRAPSectionPatchTable()
            

            wrap_patchtable.dwExternalPatchCount = 1
            wrap_patchtable.dwExternalPatchPointer = 0x1C
            
            wrap_patchtable.dwInternalPatchCount = 1
            wrap_patchtable.dwInternalPatchPointer = 0x1C
            
            wrap_patchtable.dwGlobalPatchCount = 0
            wrap_patchtable.dwGlobalPatchPointer = 0x24
            
            ExternalPatchPointerStart, InternalPatchPointerStart, GlobalPatchPointerStart = wrap_patchtable.WriteWRAPSectionPatchTable(f)
            
            
            # Writing WRAP Section (ExternalPatch)
            wrap_external_start = f.tell()
            
            wrap_external = WRAPSectionExternalPatch()
            
            for _ in range(wrap_patchtable.dwExternalPatchCount):
                wrap_external.dwPatchToTypeExternal = 1162690894 # NAME bytes in decimal, interpreted as 4-byte unsigned int
                wrap_external.dwExternalFilenameHash = b"\x00\x00\x00\x00"
                wrap_external.dwExpectedIndexExternal = 4294967295 # FF FF FF FF bytes in decimal, interpreted as 4-byte unsigned int
                wrap_external.dwPointerTargetExternal = 0xC
                
                wrap_external.WriteWRAPSectionExternalPatch(f)
               
            write_alignment_16_A1(f, f.tell())
        
            tex = TEX() # Construct TEX
            tex.ConvertToTEX(dds, Filename) # Convert to TEX
            
            tex.WriteTEX(f) # Write .wrap.tex

    
    elif Extension == 'tex':
        PathOutputDDS = os.path.join(DirectoryPath, Filename + ".dds")
        with open(Filepath, 'rb') as f:
            wrap_header = WRAPSectionHeader()
            wrap_header.ReadWRAPSectionHeader(f)

            wrap_patchtable = WRAPSectionPatchTable()
            wrap_patchtable.ReadWRAPSectionPatchTable(f)

            wrap_external = WRAPSectionExternalPatch()
            wrap_external.ReadWRAPSectionExternalPatch(f, wrap_patchtable.dwExternalPatchCount)
            
            tex = TEX()
            tex.ReadTEX(f) # Read TEX
            
        with open(PathOutputDDS, 'wb') as f:
            dds = DDS() # Construct DDS
            dds.ConvertToDDS(tex) # Convert to DDS
            
            dds.WriteDDSHeader(f) # Write DDS Header
            dds.WriteDDSData(f) # Write DDS Data
            
            
    else:
        print(f"Unsupported file type: {Extension}")