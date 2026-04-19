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

        def vertex_key(pos, normal, uvs, colors, bi, bw, tangent, binormal):
            return (
                tuple(pos),
                tuple(normal),

                tuple(tuple(uv) for uv in uvs),
                tuple(tuple(col) for col in colors),

                tuple(bi),
                tuple(bw),

                tuple(tangent),
                tuple(binormal),
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
        
        if mesh.uv_layers.active:
            mesh.calc_tangents()

        # --- Precompute per‑vertex UVs (multi‑layer) ---
        vertex_uvs = [[] for _ in range(len(mesh.vertices))]
        for layer in mesh.uv_layers:
            vert_to_uv = {}
            for loop in mesh.loops:
                vidx = loop.vertex_index
                if vidx not in vert_to_uv:          # first occurrence
                    vert_to_uv[vidx] = layer.data[loop.index].uv[:]
            for vidx, uv in vert_to_uv.items():
                vertex_uvs[vidx].append(uv)

        # --- Precompute per‑vertex colors (multi‑layer) ---
        vertex_colors = [[] for _ in range(len(mesh.vertices))]
        for layer in mesh.color_attributes:
            vert_to_color = {}
            for loop in mesh.loops:
                vidx = loop.vertex_index
                if vidx not in vert_to_color:
                    vert_to_color[vidx] = layer.data[loop.index].color[:]
            for vidx, col in vert_to_color.items():
                vertex_colors[vidx].append(col)

        # --- Now iterate over triangles ---
        for tri in mesh.loop_triangles:
            tri_indices = []
            for loop_index in tri.loops:
                loop = mesh.loops[loop_index]
                vidx = loop.vertex_index
                v = mesh.vertices[vidx]

                pos = obj.matrix_world @ v.co
                normal = tuple(mesh.vertex_normals[vidx].vector)
                
                
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

                # Correct per‑vertex UVs and colors for THIS vertex
                uv_list = vertex_uvs[vidx]      # list of tuples, one per UV layer
                color_list = vertex_colors[vidx] # list of tuples, one per color layer

                # Dedup key
                key = vertex_key(
                    pos,
                    normal,
                    uv_list,        
                    color_list,     
                    bi,
                    bw,
                    tangent,
                    binormal
                )

                # Emit vertex
                if key not in self.vertex_map:
                    idx = len(self.vertex_map)
                    self.vertex_map[key] = idx

                    positions.append(pos.copy())
                    normals.append(normal.copy())
                    tangents.append(tangent)
                    binormals.append(binormal)
                    uvs.append(uv_list)          # store only this vertex's UVs
                    colors.append(color_list)    # store only this vertex's colors
                    blend_indices.append(bi)
                    blend_weights.append(bw)
                else:
                    idx = self.vertex_map[key]

                tri_indices.append(idx)

            triangles.append(tri_indices)


        # --------------------------------------------------
        # STEP 7: STRIPIFY
        # --------------------------------------------------
        triangle_strip = make_triangle_strip(triangles, len(self.vertex_map))
        
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

