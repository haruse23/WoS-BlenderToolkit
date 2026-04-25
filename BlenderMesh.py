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
        
        if scene.flip_uv_v_avis:
            flip_uv_v_axis(bm)
            
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

        def vertex_key(pos, uv, normal):
            return (
                tuple(pos),
                

                tuple(uv),
                tuple(normal),
         

            
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
        

        mesh.calc_tangents()
        
        # --- Now iterate over triangles ---
        tri_indices = []
        for loop in mesh.loops:
            loop = mesh.loops[loop.index]
            vidx = loop.vertex_index
            v = mesh.vertices[vidx]

            matrix = obj.matrix_world
            rot = matrix.to_3x3().normalized()

            pos = matrix @ v.co # Apply all transforms to positions
            normal = (rot @ loop.normal).normalized() # Apply rotation matrix to normals, after applying scale in Blender
            # No need for inverse-transpose matrix

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
            
            vertex_uv = [uv_layers[l][loop.index] for l in range(len(uv_layers))]
            vertex_color = [color_layers[l][loop.index] for l in range(len(color_layers))]

            
            
            
            
            key = vertex_key(pos, vertex_uv, normal)
            
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
            if len(tri_indices) == 3:
                triangles.append(tri_indices)
                tri_indices = []
        

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

