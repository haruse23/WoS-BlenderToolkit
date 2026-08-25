import os
from .Hash import *
from .Wrap import *

from .DDS import *
from .TEX import *

# Use Wand Library
from wand.image import Image

from io import BytesIO

def DDSToTEX(DirectoryPath, Filename, dds):
    PathOutputTEX = os.path.join(DirectoryPath, Filename + ".wrap.tex")
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




def Convert(Filepath, compression=None, generate_mipmaps=None, mipmap_count=None):
    File = os.path.basename(Filepath)
    Filename = os.path.splitext(File)[0]
    DirectoryPath = os.path.dirname(Filepath)
    Extension = Filepath.lower().split('.')[-1].lower()
    
    Path = os.path.join(DirectoryPath, Filename)
    
    
    
    if Extension == 'dds':
        with open(Filepath, 'rb') as f:
            dds = DDS()
            dds.ReadDDSHeader(f) # Read DDS
            dds.ReadDDSData(f)
            
            DDSToTEX(DirectoryPath, Filename, dds)
    
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
            
    
    elif Extension == 'png':
        with open(Filepath, "rb") as f:
            png_data = f.read()
            
        with Image(blob=png_data) as img:
            img.compression = compression
            
            if generate_mipmaps:
                img.options["dds:mipmaps"] = mipmap_count
                
            dds = img.make_blob(format='dds') # Bytes object
            
        dds_bytes_io = BytesIO(dds)
        
        dds_object = DDS()
        dds_object.ReadDDSHeader(dds_bytes_io)
        dds_object.ReadDDSData(dds_bytes_io)
        
        DDSToTEX(DirectoryPath, Filename, dds_object)
        
    else:
        print(f"Unsupported file type: {Extension}")
        
        


def ConvertTEXToPNG(Filepath):
    File = os.path.basename(Filepath)
    Filename = os.path.splitext(File)[0]
    DirectoryPath = os.path.dirname(Filepath)
    Extension = Filepath.lower().split('.')[-1].lower()
    
    Path = os.path.join(DirectoryPath, Filename)
    
    
    if Extension == 'tex':
        with open(Filepath, 'rb') as f:
            wrap_header = WRAPSectionHeader()
            wrap_header.ReadWRAPSectionHeader(f)

            wrap_patchtable = WRAPSectionPatchTable()
            wrap_patchtable.ReadWRAPSectionPatchTable(f)

            wrap_external = WRAPSectionExternalPatch()
            wrap_external.ReadWRAPSectionExternalPatch(f, wrap_patchtable.dwExternalPatchCount)
            
            tex = TEX()
            tex.ReadTEX(f) # Read TEX
            
            
            dds = DDS() # Construct DDS
            dds.ConvertToDDS(tex) # Convert to DDS
            
            dds_data_bytes_io = BytesIO()
            dds.WriteDDSHeader(dds_data_bytes_io)
            dds.WriteDDSData(dds_data_bytes_io)
            
            # Wand
            dds_data = dds_data_bytes_io.getvalue()
            compression_format = dds.dwFourCC.decode("ascii").lower()
            mipmap_count = str(dds.dwMipMapCount)
            
            with Image(blob=dds_data) as img:
                img.format = 'png'
                
                png_data = img.make_blob()
                    
                    
        OutputPath = os.path.join(DirectoryPath, f'{Filename}.png')
        with open(OutputPath, "wb") as out:
            out.write(png_data)

        
    else:
        print(f"Unsupported file type: {Extension}")