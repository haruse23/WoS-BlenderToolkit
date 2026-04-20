import bpy
import bmesh
from .geometry_utils import *
from mathutils import Vector

class BlenderMeshExtractor:
    def __init__(self, obj, bone_mapping):
        self.obj = obj
        self.bone_mapping = bone_mapping

    def ExtractBlenderMeshData(self):

        obj = self.obj
        mesh = obj.to_mesh()
        
        uv_layers = mesh.uv_layers
        color_layers = mesh.color_attributes
        
        # --------------------------------------------------
        # STEP 1: CREATE BMESH
        # --------------------------------------------------
        
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        bmesh.ops.triangulate(bm, faces=bm.faces)
        
        scene = bpy.context.scene
        
        if scene.flip_face_normals:
            flip_face_normals_collection(bm)
            
        if scene.flip_uv:
            flip_uv_collection(bm)
        
        bm.normal_update()
        bm.to_mesh(mesh)
        bm.free()
        

        # --------------------------------------------------
        # STEP 3: GET ATTRIBUTE LAYERS
        # --------------------------------------------------
        
        
        mesh_uv_layers = list(mesh.uv_layers)
        mesh_colors_layers = list(mesh.color_attributes)

        
        # --------------------------------------------------
        # STEP 4: OUTPUT BUFFERS
        # --------------------------------------------------
        positions = []
        normals = []
        tangents = []
        binormals = []
        uvs = []
        colors = []
        blend_indices = []
        blend_weights = []
        triangles = []

        # --------------------------------------------------
        # STEP 5: DEDUP MAP
        # --------------------------------------------------
        self.vertex_map = {}

        def vertex_key(pos, uv, bi, bw):
            return (
                tuple(pos),
                

                tuple(uv),
            
             

                tuple(bi),
                tuple(bw),

            )

        """# --- COMPUTING BONE PALETTE ---
        used_groups = set()
        for vert in mesh.vertices:
            for g in vert.groups:
                used_groups.add(g.group)

        palette = []
        vertex_group_to_palette_index = {}

        armature_obj = None
        for mod in obj.modifiers:
            if mod.type == 'ARMATURE':
                armature_obj = mod.object
                break
        if armature_obj is None and obj.parent and obj.parent.type == 'ARMATURE':
            armature_obj = obj.parent

        for vg_index in sorted(used_groups):
            vg = obj.vertex_groups[vg_index]
            bone_index = armature_obj.data.bones.find(vg.name)
            if bone_index == -1:
                continue

            palette_index = len(palette)
            vertex_group_to_palette_index[vg_index] = palette_index
            palette.append(bone_index)"""
            
        
        
        
        # --------------------------------------------------
        # STEP 6: TRIANGLE EXTRACTION
        # --------------------------------------------------
        
        uv_layers = [
            [tuple(layer.data[i].uv) for i in range(len(mesh.loops))]
            for layer in mesh.uv_layers
        ]

        color_layers = [
            [tuple(layer.data[i].color) for i in range(len(mesh.loops))]
            for layer in mesh.color_attributes
        ]

        if mesh.uv_layers.active:
            mesh.calc_tangents()

        

                
        # --- Now iterate over triangles ---
        for tri in mesh.loop_triangles:
            tri_indices = []
            for loop_index in tri.loops:
                loop = mesh.loops[loop_index]
                vidx = loop.vertex_index
                v = mesh.vertices[vidx]

                pos = obj.matrix_world @ v.co
                normal = mesh.vertex_normals[vidx].vector
                
                
                if scene.flip_vertex_normals:
                        normal = (-normal[0], -normal[1], -normal[2])
                        
                normal = Vector(normal)

                # Skinning
                groups = v.groups
                groups = sorted(groups, key=lambda g: g.weight, reverse=True)[:4]
                
                bi = [self.bone_mapping.get(g.group, 0) for g in groups]
                bw = [g.weight for g in groups]
                
                total = sum(bw)
                if total > 0:
                    bw = [w / total for w in bw]
                    
                while len(bi) < 4:
                    bi.append(0)
                    bw.append(0.0)

                # Tangent space
                tangent = loop.tangent.copy()
                bitangent_sign = loop.bitangent_sign
                binormal = normal.cross(tangent) * bitangent_sign
                
                vertex_uv = [uv_layers[l][loop_index] for l in range(len(uv_layers))]
                vertex_color = [color_layers[l][loop_index] for l in range(len(color_layers))]



                
                key = vertex_key(pos, vertex_uv, bi, bw)
                
                # Emit vertex
                if key not in self.vertex_map:
                    idx = len(positions)
                    self.vertex_map[key] = idx

                    positions.append(pos.copy())
                    normals.append(normal.copy())
                    tangents.append(tangent)
                    binormals.append(binormal)
                    uvs.append(vertex_uv)
                    colors.append(vertex_color)
                    blend_indices.append(bi)
                    blend_weights.append(bw)
                else:
                    idx = self.vertex_map[key]
                
                tri_indices.append(idx)
                
            triangles.append(tri_indices)

        obj.to_mesh_clear()
        # --------------------------------------------------
        # STEP 7: STRIPIFY
        # --------------------------------------------------
        triangle_strip = make_triangle_strip(triangles, len(positions))
        
        # --------------------------------------------------
        # STEP 8: RETURN EVERYTHING
        # --------------------------------------------------
        return {
            "positions": positions,
            "normals": normals,
            "tangents": tangents,
            "binormals": binormals,
            "uvs": uvs,
            "colors": colors,
            "blend_indices": blend_indices,
            "blend_weights": blend_weights,
            "triangle_strip": triangle_strip,
            "triangle_list": triangles,
        }

