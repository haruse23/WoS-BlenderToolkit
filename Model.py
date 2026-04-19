from enum import Enum
from .Helpers import *
import io

class D3DDECLTYPE(Enum):
    _0 = "<1f" # D3DDECLTYPE_FLOAT1     
    _1 = "<2f" # D3DDECLTYPE_FLOAT2
    _2 = "<3f" # D3DDECLTYPE_FLOAT3
    _3 = "<4f" # D3DDECLTYPE_FLOAT4
    _4 = "<4B" #D3DDECLTYPE_D3DCOLOR
    _5 = "<4B" #D3DDECLTYPE_UBYTE4
    _6 = "<2h" #D3DDECLTYPE_SHORT2
    _7 = "<4h" #D3DDECLTYPE_SHORT4
    _8 = "<4B" #D3DDECLTYPE_UBYTE4N
    _9 = "<2h" #D3DDECLTYPE_SHORT2N
    _10 = "<4h" #D3DDECLTYPE_SHORT4N
    _11 = "<2H" #D3DDECLTYPE_USHORT2N
    _12 = "<4H" #D3DDECLTYPE_USHORT4N
    _13 = "" #D3DDECLTYPE_UDEC3
    _14 = "" #D3DDECLTYPE_DEC3N
    _15 = "" #D3DDECLTYPE_FLOAT16_2
    _16 = "" #D3DDECLTYPE_FLOAT16_4
    
    _17 = "" #D3DDECLTYPE_UNUSED





class D3DDECLUSAGE(Enum):
    _0 = "POSITION" # D3DDECLUSAGE_POSITION
    _1 = "BLENDWEIGHT" # D3DDECLUSAGE_BLENDWEIGHT
    _2 = "BLENDINDICES" # D3DDECLUSAGE_BLENDINDICES
    _3 = "NORMAL" # D3DDECLUSAGE_NORMAL
    _4 = "PSIZE" # D3DDECLUSAGE_PSIZE
    _5 = "TEXCOORD" # D3DDECLUSAGE_TEXCOORD
    _6 = "TANGENT" # D3DDECLUSAGE_TANGENT
    _7 = "BINORMAL" # D3DDECLUSAGE_BINORMAL
    _8 = "TESSFACTOR" # D3DDECLUSAGE_TESSFACTOR
    _9 = "POSITIONT" # D3DDECLUSAGE_POSITIONT
    _10 = "COLOR" # D3DDECLUSAGE_COLOR
    _11 = "FOG" # D3DDECLUSAGE_FOG
    _12 = "DEPTH" # D3DDECLUSAGE_DEPTH
    _13 = "SAMPLE" # D3DDECLUSAGE_SAMPLE

    
    


class ModelHeader():
    def __init__(self):
        self.dwFilenamePointer = 0
        self.dwFilenameHash = 0
        self.dwParsedFlag = 0
        self.dwMeshCount = 0
        
        self.MeshTablePointerPOS = 0 # For Reading Model
        
        self.dwMeshTablePointer = 0
        self.dwSkeletonDataPointer = 0
        self.ExternalMeshCount = 0
        
        self.ExternalMeshTablePointerPOS = 0 # For Reading Model
        self.ExternalMeshTablePointer = 0
        
        self.ModelOffsetX = 0 # Add to position X
        self.ModelOffsetY = 0 # Add to position Y
        self.ModelOffsetZ = 0 # Add to position Z
        self.ModelBoundingSphereRadius= 0
        
        self.fpModelBBoxX = 0
        self.fpModelBBoxY = 0
        self.fpModelBBoxZ = 0
        self.fpModelBBoxW = 0
        
        
        
    def ReadModelHeader(self, f):
        self.dwFilenamePointer = read_uint(f)
        self.dwFilenameHash = read_uint(f)
        self.dwParsedFlag = read_uint(f)
        self.dwMeshCount = read_uint(f)
        
        self.MeshTablePointerPOS = f.tell() # For Reading Model
        
        self.dwMeshTablePointer = read_uint(f)
        self.dwSkeletonDataPointer = read_uint(f)
        self.ExternalMeshCount = read_uint(f)
        
        self.ExternalMeshTablePointerPOS = f.tell()
        self.ExternalMeshTablePointer = read_uint(f)
        
        self.ModelOffsetX = read_float(f)
        self.ModelOffsetY = read_float(f)
        self.ModelOffsetZ = read_float(f)
        self.ModelBoundingSphereRadius = read_float(f)
        
        self.fpModelBBoxX = read_float(f)
        self.fpModelBBoxY = read_float(f)
        self.fpModelBBoxZ = read_float(f)
        self.fpModelBBoxW = read_float(f)
        
        
    def WriteModelHeader(self, f):
        write_uint(f, self.dwFilenamePointer) # Filename Pointer
        write_uint(f, self.dwFilenameHash)
        write_uint(f, self.dwParsedFlag) # Parsed Flag
        write_uint(f, self.dwMeshCount)
        
        MeshTablePointerStart = f.tell() # For Writing Model
        write_uint(f, self.dwMeshTablePointer) # MeshTablePointer
        write_uint(f, self.dwSkeletonDataPointer) # SkeletonDataPointer
        write_uint(f, self.ExternalMeshCount) # Unknown1
        write_uint(f, self.ExternalMeshTablePointer) # Unknown2
        
        write_float(f, self.ModelOffsetX)
        write_float(f, self.ModelOffsetY)
        write_float(f, self.ModelOffsetZ)
        write_float(f, self.ModelBoundingSphereRadius)
        
        write_float(f, self.fpModelBBoxX)
        write_float(f, self.fpModelBBoxY)
        write_float(f, self.fpModelBBoxZ)
        write_float(f, self.fpModelBBoxW) # ModelBBoxW
        
        return MeshTablePointerStart # For Writing Model
        
       
        
        
        
        
        
class MeshTable():
    def __init__(self):
        self.dwParsedFlag = 0
        
        self.MeshInfoPointerPOS = 0 # For Reading Model
        
        self.dwMeshInfoPointer = 0
        
        self.MeshInfoPointerStart = [] # For Writing Model
        
        
    def ReadMeshTable(self, f):
        self.dwParsedFlag = read_uint(f)  

        self.MeshInfoPointerPOS = f.tell() # For Reading Model
         
        self.dwMeshInfoPointer = read_uint(f)
        
    
    def WriteMeshTable(self, f):
        write_uint(f, self.dwParsedFlag) # Parsed Flag
        
        self.MeshInfoPointerStart.append(f.tell()) # For Writing Model
        write_uint(f, self.dwMeshInfoPointer) # MeshInfoPointer
        
        
        
    #def BackpatchMeshTable(self, f, MeshInfoPointer):
        #for offset, mip in zip(self.MeshInfoPointerPos, MeshInfoPointer):
            #f.seek(offset, 0)
            #write_uint(f, mip)  
        
        
        
        
        
        
class MeshInfo():
    def __init__(self):
        self.MeshOffsetX = 0
        self.MeshOffsetY = 0
        self.MeshOffsetZ = 0
        self.MeshBoundingSphereRadius = 0
        
        self.fpMeshBBoxX = 0
        self.fpMeshBBoxY = 0
        self.fpMeshBBoxZ = 0
        self.fpMeshBBoxW = 0
        
        
        
        self.dwMaterialDataPointer = 0
        
        self.BonePalettePointerPOS = 0 # For Reading Model
        
        self.dwBonePalettePointer = 0
        self.dwBonePaletteIndexCount = 0
        
        self.VertexBufferPointerPOS = 0 # For Reading Model
        self.dwVertexBufferPointer = 0
        
        self.Unknown1 = 0
        self.dwVertexCount = 0
        self.Unknown2 = 0
        self.dwIndexBufferPointer = 0
        
        self.Unknown3 = 0
        self.dwIndexCount = 0
        self.dwIndexSize = 0
        
        self.SchemaTablePointerPOS = 0 # For Reading Model
        
        self.dwSchemaTablePointer = 0
        
        
        self.MaterialDataPointerStart = [] # For Writing Model
        
        self.BonePalettePointerStart = [] # For Writing Model
        self.VertexBufferPointerStart = [] # For Writing Model
        self.IndexBufferPointerStart = [] # For Writing Model
        self.SchemaTablePointerStart = [] # For Writing Model
        
        
    def ReadMeshInfo(self, f):
        self.MeshOffsetX = read_float(f)
        self.MeshOffsetY = read_float(f)
        self.MeshOffsetZ = read_float(f)
        self.MeshBoundingSphereRadius = read_float(f)
        
        self.fpMeshBBoxX = read_float(f)
        self.fpMeshBBoxY = read_float(f)
        self.fpMeshBBoxZ = read_float(f)
        self.fpMeshBBoxW = read_float(f)
        
        
        
        self.dwMaterialDataPointer = read_uint(f)
        
        self.BonePalettePointerPOS = f.tell() # For Reading Model
        
        self.dwBonePalettePointer = read_uint(f)
        self.dwBonePaletteIndexCount = read_uint(f)
        
        self.VertexBufferPointerPOS = f.tell()
        self.dwVertexBufferPointer = read_uint(f)
        
        self.Unknown1 = read_uint(f)
        self.dwVertexCount = read_uint(f)
        self.Unknown2 = read_uint(f)
        self.dwIndexBufferPointer = read_uint(f)
        
        self.Unknown3 = read_uint(f)
        self.dwIndexCount = read_uint(f)
        self.dwIndexSize = read_uint(f)
        
        self.SchemaTablePointerPOS = f.tell() # For Reading Model
        
        self.dwSchemaTablePointer = read_uint(f)
        
        
    def WriteMeshInfo(self, f):
        write_float(f, self.MeshOffsetX)
        write_float(f, self.MeshOffsetY)
        write_float(f, self.MeshOffsetZ)
        write_float(f, self.MeshBoundingSphereRadius)
        
        write_float(f, self.fpMeshBBoxX)
        write_float(f, self.fpMeshBBoxY)
        write_float(f, self.fpMeshBBoxZ)
        write_float(f, self.fpMeshBBoxW)
        
        self.MaterialDataPointerStart.append(f.tell()) # For Writing Model
        write_uint(f, self.dwMaterialDataPointer) # MaterialDataPointer
        
        self.BonePalettePointerStart.append(f.tell()) # For Writing Model
        write_uint(f, self.dwBonePalettePointer) # BonePalettePointer
        
        write_uint(f, self.dwBonePaletteIndexCount)
        
        self.VertexBufferPointerStart.append(f.tell()) # For Writing Model
        write_uint(f, self.dwVertexBufferPointer) # VertexBufferPointer
        
        write_uint(f, self.Unknown1) # Unknown 2
        
        write_uint(f, self.dwVertexCount)
        
        write_uint(f, self.Unknown2) # Unknown 3
        
        self.IndexBufferPointerStart.append(f.tell()) # For Writing Model
        write_uint(f, self.dwIndexBufferPointer) # IndexBufferPointer
        
        write_uint(f, self.Unknown3) # Unknown 4
        write_uint(f, self.dwIndexCount)
        write_uint(f, self.dwIndexSize) # Index Size
        
        self.SchemaTablePointerStart.append(f.tell()) # For Writing Model
        write_uint(f, self.dwSchemaTablePointer) # SchemaTablePointer
        
        
        
        """def BackpatchMeshInfo(self, f, BonePalettePointer, VertexBufferPointer, IndexBufferPointer, SchemaTablePointer):
          for offset, bpp in zip(self.BonePalettePointerPos, BonePalettePointer):
            f.seek(offset, 0)
            write_uint(f, bpp)
        
          for offset, vbp in zip(self.VertexBufferPointerPos, VertexBufferPointer):
            f.seek(offset, 0)
            write_uint(f, vbp)
        
          for offset, ibp in zip(self.IndexBufferPointerPos, IndexBufferPointer):
            f.seek(offset, 0)
            write_uint(f, ibp)
        
          for offset, stp in zip(self.SchemaTablePointerPos, SchemaTablePointer):
            f.seek(offset, 0)
            write_uint(f, stp)"""
        
        
        
        

class SchemaTable():
    def __init__(self):
        self.dwVertexStride = 0
        
        self.VertexSchemaPointerPOS = 0 # For Reading Model
        
        self.VertexSchemaPointerStart = [] # For Writing Model
        
        self.dwVertexSchemaPointer = 0
        self.Unknown = 0
        
    def ReadSchemaTable(self, f):
        self.dwVertexStride = read_uint(f)
        
        self.VertexSchemaPointerPOS = f.tell() # For Reading Model
        
        self.dwVertexSchemaPointer = read_uint(f)
        self.Unknown = read_uint(f)
        
    def WriteSchemaTable(self, f):
        write_uint(f, self.dwVertexStride)
        
        self.VertexSchemaPointerStart.append(f.tell()) # For Writing Model
        write_uint(f, self.dwVertexSchemaPointer)
        write_uint(f, self.Unknown)

    
        
        
    """def BackpatchSchemaTable(self, f, VertexStride, VertexSchemaPointer):
            write_uint(f, VertexStride)
            write_uint(f, VertexSchemaPointer)"""
            
        
        
        

class VertexSchema():
    def __init__(self):
        self.wStream = 0
        self.wOffset = 0
        self.bType = 0
        self.bMethod = 0
        self.bUsage = 0
        self.bUsageIndex = 0
        
        
    def ReadVertexSchema(self, peek):
        self.wStream = struct.unpack_from("<H", peek, 0)[0]
        self.wOffset = struct.unpack_from("<H", peek, 2)[0]
        self.bType = struct.unpack_from("<B", peek, 4)[0]
        self.bMethod = struct.unpack_from("<B", peek, 5)[0]
        self.bUsage = struct.unpack_from("<B", peek, 6)[0]
        self.bUsageIndex = struct.unpack_from("<B", peek, 7)[0]
        
    
    def WriteVertexSchema(self, f):  
        write_ushort(f, self.wStream) # Stream
        write_ushort(f, self.wOffset) # Offset
        write_ubyte(f, self.bType) # Type
        write_ubyte(f, self.bMethod) # Method
        write_ubyte(f, self.bUsage) # Usage
        write_ubyte(f, self.bUsageIndex) # UsageIndex
        
        
        
    """def BackpatchVertexSchema(self, f, first_vertex_schema_pos, Offset, Type, Usage):
            f.seek(first_vertex_schema_pos, 0)
            
            for offset, type, usage in zip(Offset, Type, Usage):
                f.write(b'\x00' * 2) # Stream
                write_ushort(f, offset) # Offset
                write_ubyte(f, type) # Type
                f.write(b'\x00') # Method
                write_ubyte(f, usage) # Usage
                write_ubyte(f, 0) # UsageIndex"""
         
        
        
class VertexBuffer():
    def __init__(self):
        self.Positions = []
        self.BlendWeights = []
        self.BlendIndices = []
        self.Normals = []
        self.TexCoords = {}
        self.Tangents = []
        self.Binormals = []
        self.Colors = {}  
        
        self.Attributes = []
        
        
class VertexAttribute:
    def __init__(self):
        self.Buffer = None # Store a reference to parent
        self.Offset = 0
        self.Type = 0
        self.Usage = 0
        self.UsageIndex = 0
        
      
        
    def ReadVertexAttribute(self, vertex_schema, model_header, f): 
        self.Type = vertex_schema.bType
        self.Usage = D3DDECLUSAGE["_" + str(vertex_schema.bUsage)].value
        self.UsageIndex = vertex_schema.bUsageIndex
         
        if self.Usage == "POSITION":
            ModelBBoxX = model_header.fpModelBBoxX
            ModelBBoxY = model_header.fpModelBBoxY
            ModelBBoxZ = model_header.fpModelBBoxZ
            ModelBBoxW = model_header.fpModelBBoxW
            
            ModelOffsetX = model_header.ModelOffsetX
            ModelOffsetY = model_header.ModelOffsetY
            ModelOffsetZ = model_header.ModelOffsetZ
            
            position_data = FetchAndReadDataType(f, self.Type)
            
            px = position_data[0] / 32767 * ModelBBoxX + ModelOffsetX
            py = position_data[1] / 32767 * ModelBBoxY + ModelOffsetY
            pz = position_data[2] / 32767 * ModelBBoxZ + ModelOffsetZ
            pw = 0
            
            self.Buffer.Positions.append((px, py, pz))
            
        if self.Usage == "BLENDWEIGHT":
            bw1, bw2, bw3, bw4 = FetchAndReadDataType(f, self.Type)
            
            self.Buffer.BlendWeights.append((bw1, bw2, bw3, bw4))
            
        if self.Usage == "BLENDINDICES":
            bi1, bi2, bi3, bi4 = FetchAndReadDataType(f, self.Type)
            
            self.Buffer.BlendIndices.append((bi1, bi2, bi3, bi4))
            
        if self.Usage == "NORMAL":
            normal_data = FetchAndReadDataType(f, self.Type)
            
            nx = normal_data[0]
            ny = normal_data[1]
            nz = normal_data[2]
            
            
            
            self.Buffer.Normals.append((nx, ny, nz))
            
        if self.Usage == "TEXCOORD":
            texcoord_data = FetchAndReadDataType(f, self.Type)
            
            tc1 = texcoord_data[0]
            tc2 = texcoord_data[1]
            
            if self.UsageIndex not in self.Buffer.TexCoords:
                self.Buffer.TexCoords[self.UsageIndex] = []
                
            self.Buffer.TexCoords[self.UsageIndex].append((tc1, tc2))
            
        if self.Usage == "TANGENT":
            tangent_data = FetchAndReadDataType(f, self.Type)
            
            tx = tangent_data[0]
            ty = tangent_data[1]
            tz = tangent_data[2]
            
            self.Buffer.Tangents.append((tx, ty, tz))
            
        if self.Usage == "BINORMAL":
            binormal_data = FetchAndReadDataType(f, self.Type)
            
            bnx = binormal_data[0]
            bny = binormal_data[1]
            bnz = binormal_data[2]
            
            self.Buffer.Binormals.append((bnx, bny, bnz))
            
        if self.Usage == "COLOR":
            c1, c2, c3, c4 = FetchAndReadDataType(f, self.Type)
            
            if self.UsageIndex not in self.Buffer.Colors:
                self.Buffer.Colors[self.UsageIndex] = []
                
            self.Buffer.Colors[self.UsageIndex].append((c1, c2, c3, c4))
                
                
    def WriteVertexAttribute(self, f, vertex_count, positions, normals, tangents, binormals, uvs, colors, blend_indices, blend_weights, ModelBBox, BonePaletteCount):

        for i in range(vertex_count):
            if attribute_exists(uvs):
                  for j in range(len(uvs[i])):  # each UV channel
                    UV = uvs[i][j]
        
                    u = UV[0]
                    v = UV[1]
                  
                    u = convert_float_to_half_float_numpy(u)
                    v = convert_float_to_half_float_numpy(v)
                  
                    f.write(u + v)
                  
            if attribute_exists(tangents):
                  T = tangents[i]
                  
                  tx = T.x
                  ty = T.y
                  tz = T.z
                  tw = 0
                  
                  tx = convert_float_to_half_float_numpy(tx)
                  ty = convert_float_to_half_float_numpy(ty)
                  tz = convert_float_to_half_float_numpy(tz)
                  tw = convert_float_to_half_float_numpy(tw)

                  
                  f.write(tx + ty + tz + tw)
              
            if attribute_exists(positions):
                  ModelBBoxX = ModelBBox[0]
                  ModelBBoxY = ModelBBox[1]
                  ModelBBoxZ = ModelBBox[2]
                  ModelBBoxW = 0
                    
                  P = positions[i]
                  
                  px = P.x
                  py = P.y
                  pz = P.z
                  pw = 0
                  
                  px = px / ModelBBoxX
                  py = py / ModelBBoxY
                  pz = pz / ModelBBoxZ
                  pw = 0
                  
                  px = px * 32767
                  py = py * 32767
                  pz = pz * 32767
                  pw = 0
                  
                  px = int(round(px))
                  py = int(round(py))
                  pz = int(round(pz))
                  pw = int(round(pw))
                  
                  f.write(struct.pack("<4h", px, py, pz, pw))
              
            if attribute_exists(normals):
                  N = normals[i]
                  
                  nx = N.x
                  ny = N.y
                  nz = N.z
                  nw = 0.0
                  
                  nx = convert_float_to_half_float_numpy(nx)
                  ny = convert_float_to_half_float_numpy(ny)
                  nz = convert_float_to_half_float_numpy(nz)
                  nw = convert_float_to_half_float_numpy(nw)
                  
                  f.write(nx + ny + nz + nw)
              
              
            
              
          
          
              
          
              
              
            if attribute_exists(colors):
                  for j in range(len(colors[i])):  # each Color channel
                    C = colors[i][j]
                  
                    r = C[0]
                    g = C[1]
                    b = C[2]
                    a = C[3] if len(C) > 3 else 1.0
                      
                    r = r * 255
                    g = g * 255
                    b = b * 255
                    a = a * 255
                      
                    r = int(round(r))
                    g = int(round(g))
                    b = int(round(b))
                    a = int(round(a))
                      
                    f.write(struct.pack("<4B", r, g, b, a))
              
              
            if BonePaletteCount:
                  # Blend Weights
                  BW = blend_weights[i]
                  
                  bw1 = BW[0]
                  bw2 = BW[1]
                  bw3 = BW[2]
                  bw4 = BW[3]
                  
                  bw1 = bw1 * 255
                  bw2 = bw2 * 255
                  bw3 = bw3 * 255
                  bw4 = bw4 * 255
                  
                  bw1 = int(round(bw1))
                  bw2 = int(round(bw2))
                  bw3 = int(round(bw3))
                  bw4 = int(round(bw4))
                  
                  """if i == 1529:
                    print("RAW BW:", BW)
                    print("SCALED:", [b * 255 for b in BW])
                    print("FINAL BYTES:", [
                        int(round(b * 255)) for b in BW
                    ])"""
                                  
                  f.write(struct.pack("<4B", bw1, bw2, bw3, bw4))
                  
                  # Blend Indices
                  BI = blend_indices[i]
                  
                  bi1 = BI[0]
                  bi2 = BI[1]
                  bi3 = BI[2]
                  bi4 = BI[3]
                  
                  f.write(struct.pack("<4B", bi1, bi2, bi3, bi4))
              
              
              
            if attribute_exists(binormals):
                  B = binormals[i]
                  
                  bnx = B.x
                  bny = B.y
                  bnz = B.z
                  bnw = 0
                  
                  bnx = convert_float_to_half_float_numpy(bnx)
                  bny = convert_float_to_half_float_numpy(bny)
                  bnz = convert_float_to_half_float_numpy(bnz)
                  bnw = convert_float_to_half_float_numpy(bnw)
                  
                  f.write(bnx + bny + bnz + bnw)
              
              
              
              
              
              
              

              
        
            
        
        
class IndexBuffer():
    def __init__(self):
        self.Index = 0
        self.Indices = []
        
        
        
    def ReadIndex(self, f, VertexCount):
        if VertexCount > 65535:
            self.Index = read_uint(f)
            
        else:
            self.Index = read_ushort(f)
        self.Indices.append(self.Index)
        
    
    def WriteIndices(self, f, VertexCount):
        for index in self.Indices:
            if VertexCount > 65535:
                write_uint(f, index)
            
            else:
                write_ushort(f, index)
            
        
        
        
        
        