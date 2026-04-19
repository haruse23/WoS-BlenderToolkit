from .Model import *
from .Wrap import *

# filepath = r"D:\WebOfShadowsTools-master\python\extracted_pcpack_wolverine\S_WOLVERINE\0x991E9D0E.s1_wolverine000.standalone_mesh"
def ReadModel(filepath):
    with open(filepath, "rb") as f:
        Model = []
        
        wrap_header = WRAPSectionHeader()
        
        wrap_header.ReadWRAPSectionHeader(f)
        
        
        wrap_patchtable = WRAPSectionPatchTable()
        
        wrap_patchtable.ReadWRAPSectionPatchTable(f)

  
        wrap_external = WRAPSectionExternalPatch()
        
        wrap_external.ReadWRAPSectionExternalPatch(f, wrap_patchtable.dwExternalPatchCount)
        
        
        wrap_internal = WRAPSectionInternalPatch()
        
        wrap_internal.ReadWRAPSectionInternalPatch(f, wrap_patchtable.dwInternalPatchCount)
        
 
 
        model_header = ModelHeader()
        
        model_header.ReadModelHeader(f)
        
        

        
        for m in range(model_header.dwMeshCount):
            f.seek(model_header.MeshTablePointerPOS + model_header.dwMeshTablePointer + m * 0x8, 0) # Seek to Model Table
                    
            mesh_table = MeshTable()
            
            mesh_table.ReadMeshTable(f)
            
            f.seek(mesh_table.MeshInfoPointerPOS + mesh_table.dwMeshInfoPointer, 0)
            

            mesh_info = MeshInfo()
            
            mesh_info.ReadMeshInfo(f)
            
            bone_palette_indices = []
            if mesh_info.dwBonePalettePointer != 0:
                f.seek(mesh_info.BonePalettePointerPOS + mesh_info.dwBonePalettePointer, 0)
 
                for bpi in range(mesh_info.dwBonePaletteIndexCount):
                    bone_palette_index = read_ushort(f)
                    bone_palette_indices.append(bone_palette_index)
                    
                print(bone_palette_indices)
            
            print(mesh_info.dwIndexSize)
            
            f.seek(mesh_info.SchemaTablePointerPOS + mesh_info.dwSchemaTablePointer, 0)
            
            print(f.tell())
            
            schema_table = SchemaTable()
            
            schema_table.ReadSchemaTable(f)

            f.seek(schema_table.VertexSchemaPointerPOS + schema_table.dwVertexSchemaPointer, 0)
            
            print(f.tell())
                
            vertex_declaration = []
            while True:
                peek = f.read(8)
                
                if peek == b'\xFF\x00\x00\x00\x11\x00\x00\x00': # Vertex Schema Sentinel
                    break

                vertex_schema = VertexSchema()
                
                vertex_schema.ReadVertexSchema(peek)
                
                vertex_declaration.append(vertex_schema)
                
                print(peek)
                
          
            if model_header.ExternalMeshTablePointer != 0:
                f.seek(model_header.ExternalMeshTablePointerPOS + model_header.ExternalMeshTablePointer, 0)
                
                for i in range(model_header.ExternalMeshCount):
                    f.read(8)
                
            
            
            print(f.tell())
            
            Model.append((mesh_table, mesh_info, bone_palette_indices, schema_table, vertex_declaration))
            

        
            

        Vertex_Buffers = []
        Index_Buffers = []
        print(f.tell())
        f.seek(Model[0][1].VertexBufferPointerPOS + Model[0][1].dwVertexBufferPointer, 0)
        for Mesh in Model:
            vertex_buffer = VertexBuffer()
            for v in range(Mesh[1].dwVertexCount):
                #print(Mesh[1].dwVertexCount)
                for vertex_schema in Mesh[4]: # vertex_declaration
                    vertex_attribute = VertexAttribute()
                    
                    vertex_attribute.Buffer = vertex_buffer
                    
                    vertex_attribute.ReadVertexAttribute(vertex_schema, model_header, f)

            Vertex_Buffers.append(vertex_attribute.Buffer)
            print(f.tell())   
            align_to_4(f, f.tell())
            print(f.tell())
            index_buffer = IndexBuffer()
            for id in range(Mesh[1].dwIndexCount):

                
                index_buffer.ReadIndex(f, Mesh[1].dwVertexCount)
                
            Index_Buffers.append(index_buffer)
            print(f.tell())
            align_to_4(f, f.tell())
            print(f.tell())
   
   
    return Model, Vertex_Buffers, Index_Buffers, wrap_external
        
#    for i, M in enumerate(Model):
#        print(f"VertexCount: {Model[i][1].dwVertexCount}")
       
    
#    for vb in Vertex_Buffers:
#        print(vb.Positions) 

#    for ib in Index_Buffers:
#         print(ib.Indices)
        
#    for i, M in enumerate(Model):
#        for k in range(len(Model[i][4])):
#            print(Model[i][4][k].bType)
#            print(Model[i][4][k].bUsage)


# ReadModel(filepath)
                
                
            

          
        
        