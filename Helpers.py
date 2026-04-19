import struct
import re
import math
from mathutils import Matrix, Vector, Quaternion
import numpy as np

from .BlenderMesh import *    

def read_ubyte(f):
    return struct.unpack("<B", f.read(1))[0]

def read_ushort(f):
    return struct.unpack("<H", f.read(2))[0]

def read_vertex_position_short(f):
    return struct.unpack("<h", f.read(2))[0]

def read_uint(f):
    return struct.unpack("<I", f.read(4))[0]


def read_float(f):
    return struct.unpack("<f", f.read(4))[0]

def read_bytes(f, format):
    match = re.search(r'\d+', format)
    return struct.unpack(format, f.read(int(match.group())))

def convert_half_float_to_float(f):
    """
    Read 2 bytes (half-float) and return as Python float.
    """
    
    # Unpack as 16-bit unsigned integer
    h = struct.unpack('<H', f.read(2))[0]  # Little-endian

    # Convert half-float to float
    s = (h >> 15) & 0x00000001    # sign
    e = (h >> 10) & 0x0000001F    # exponent
    f = h & 0x000003FF             # fraction

    if e == 0:
        if f == 0:
            # Zero
            return float((-1)**s * 0.0)
        else:
            # Subnormal number
            return (-1)**s * (f / 1024) * 2**(-14)
    elif e == 31:
        # Inf or NaN
        return float('inf') if f == 0 else float('nan')
    else:
        # Normalized number
        return (-1)**s * (1 + f / 1024) * 2**(e - 15)


def convert_float_to_half_float(value):
    """
    Convert a Python float to a 16-bit half-float representation (as bytes).
    Returns a bytes object of length 2.
    """

    f = float(value)

    if math.isnan(f):
        h = 0x7E00  # standard half-float NaN
    elif math.isinf(f):
        h = 0x7C00 if f > 0 else 0xFC00
    elif f == 0.0:
        # Preserve sign
        h = 0x8000 if math.copysign(1.0, f) < 0 else 0x0000
    else:
        # Normalized or subnormal number
        s = 0
        if f < 0:
            s = 1
            f = -f

        # Get exponent and fraction
        e = int(math.floor(math.log(f, 2)))
        if e < -14:
            # Subnormal
            f_frac = int(round(f / 2**(-24)))  # f / 2^-24 for 10-bit fraction
            h = (s << 15) | f_frac
        elif e > 15:
            # Overflow → Inf
            h = (s << 15) | (0x1F << 10)
        else:
            # Normalized
            frac = f / (2 ** e) - 1.0
            f_frac = int(round(frac * 1024))  # 10-bit fraction
            h = (s << 15) | ((e + 15) << 10) | (f_frac & 0x3FF)

    return struct.pack('<H', h)


def convert_float_to_half_float_numpy(value):
    return np.float16(value).tobytes()
    
def convert_half_float_to_float_numpy(data):
    return np.frombuffer(data, dtype='<f2').astype(np.float32)
    

def write_ubyte(f, data):
    f.write(struct.pack("<B", data))
    
def write_uint(f, data):
    f.write(struct.pack("<I", data))
    
def write_ushort(f, data):
    f.write(struct.pack("<H", data))
    
def write_float(f, data):
    f.write(struct.pack("<f", data))


def align_to_4(f, offset):
    alignment_bytes = (4 - (offset % 4)) % 4
    f.seek(alignment_bytes, 1)
    
def align_to_16(f, offset):
    alignment_bytes = (16 - (offset % 16)) % 16
    f.seek(alignment_bytes, 1)
    
def write_alignment_4(f, offset):
    alignment_bytes = (4 - (offset % 4)) % 4
    if alignment_bytes:
        f.write(b'\x00' * alignment_bytes)
        
def write_alignment_16(f, offset):
    alignment_bytes = (16 - (offset % 16)) % 16
    if alignment_bytes:
        f.write(b'\x00' * alignment_bytes)
        
def write_alignment_16_A1(f, offset):
    alignment_bytes = (16 - (offset % 16)) % 16
    if alignment_bytes:
        f.write(b'\xA1' * alignment_bytes)
    
def convert_triangle_strips_to_triangle_list(indices):
    triangle_list = []

    for i in range(len(indices) - 2):
        a, b, c = indices[i], indices[i+1], indices[i+2]
        
        # Skip degenerate triangles
        if a == b or b == c or a == c:
            continue
        
        # Determine winding: flip every other triangle
        if i % 2 == 0:
            triangle_list.append([a, b, c])
        else:
            triangle_list.append([b, a, c])
            
    return triangle_list




def FetchAndReadDataType(f, DataType):
    if DataType == 0:
        raise ValueError(f"Invalid DataType {DataType} at file pos {f.tell()}")
        return struct.unpack("<f", f.read(4))[0]
    
    if DataType == 1:
        return struct.unpack("<2f", f.read(8))
    
    if DataType == 2:
        return struct.unpack("<3f", f.read(12))

    if DataType == 3:
        return struct.unpack("<4f", f.read(16))
    
    if DataType == 4:
        return struct.unpack("<4B", f.read(4))
    
    if DataType == 5:
        return struct.unpack("<4B", f.read(4))
    
    if DataType == 6:
        return struct.unpack("<2h", f.read(4))
    
    if DataType == 7:
        return struct.unpack("<4h", f.read(8))
    
    if DataType == 8:
        value1, value2, value3, value4 = struct.unpack("<4B", f.read(4))
        
        value1 = value1 / 255
        value2 = value2 / 255
        value3 = value3 / 255
        value4 = value4 / 255
        return (value1, value2, value3, value4)
    
    if DataType == 9:
        value1, value2 = struct.unpack("<2h", f.read(4))
        
        value1 = value1 / 32767
        value2 = value2 / 32767
        
        return (value1, value2)
    
    if DataType == 10:
        value1, value2, value3, value4 = struct.unpack("<4h", f.read(8))
   
        
        return (value1, value2, value3, value4)
    
    if DataType == 11:
        value1, value2 = struct.unpack("<2H", f.read(4))
        
        value1 = value1 / 65535
        value2 = value2 / 65535
        
        return (value1, value2)
    
    if DataType == 12:
        value1, value2, value3, value4 = struct.unpack("<4H", f.read(8))
        
        value1 = value1 / 65535
        value2 = value2 / 65535
        value3 = value3 / 65535
        value4 = value4 / 65535
        
        return (value1, value2, value3, value4)


    if DataType == 15:
        value1 = convert_half_float_to_float_numpy(f.read(2))
        value2 = convert_half_float_to_float_numpy(f.read(2))
        
        return (value1, value2)
    
    if DataType == 16:
        value1 = convert_half_float_to_float_numpy(f.read(2))
        value2 = convert_half_float_to_float_numpy(f.read(2))
        value3 = convert_half_float_to_float_numpy(f.read(2))
        value4 = convert_half_float_to_float_numpy(f.read(2))
        
        return (value1, value2, value3, value4)
    
    
  
  
def attribute_exists(attr):
    """
    True only if there is REAL non-empty data anywhere inside.
    Handles nested lists (UV sets, colors, skin data).
    """

    if attr is None:
        return False

    if isinstance(attr, (list, tuple)):
        for x in attr:
            if attribute_exists(x):   # recursion
                return True
        return False

    # base case: real value (Vector, float, tuple, etc.)
    return True



def has_skinning(blend_indices, blend_weights):
    if not blend_indices or not blend_weights:
        return False

    for bi, bw in zip(blend_indices, blend_weights):
        for w in bw:
            if w > 0.0:
                return True
    return False



    
    
    
    
    
def FetchBlenderData(mesh_objects):
    # =========================
    # 1. HELPERS
    # =========================

    import math

    def compute_bounds(positions):
        def dist(a, b):
            return math.sqrt(
                (a[0] - b[0])**2 +
                (a[1] - b[1])**2 +
                (a[2] - b[2])**2
            )

        def normalize(v):
            length = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
            if length == 0:
                return (0.0, 0.0, 0.0)
            return (v[0]/length, v[1]/length, v[2]/length)

        # -------- AABB (your original code) --------
        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]
        zs = [p[2] for p in positions]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)

        ModelBBox = (
            max(abs(min_x), abs(max_x)),
            max(abs(min_y), abs(max_y)),
            max(abs(min_z), abs(max_z))
        )
        
        MeshBBox = (
            (max_x - min_x) / 2,
            (max_y - min_y) / 2,
            (max_z - min_z) / 2
        )

        model_bsphere_radius = math.sqrt(
                ModelBBox[0] ** 2 +
                ModelBBox[1] ** 2 +
                ModelBBox[2] ** 2
            )
            
        mesh_bsphere_radius = math.sqrt(
                MeshBBox[0] ** 2 +
                MeshBBox[1] ** 2 +
                MeshBBox[2] ** 2
            )

        return {
            "min": (min_x, min_y, min_z),
            "max": (max_x, max_y, max_z),
            
            "model_bsphere_radius": model_bsphere_radius,
            "mesh_bsphere_radius": mesh_bsphere_radius,

            "ModelBBox": ModelBBox,
            "MeshBBox": MeshBBox
        }

    def build_attributes(mesh_dict, BonePaletteCount):
        attributes = []
        offset = []
        type_ = []
        usage = []
        usage_index = []
        
        def add(attr_type, attr_usage, attr_usage_index, size):
            offset.append(attributes[0][1] if attributes else 0)
            type_.append(attr_type)
            usage.append(attr_usage)
            usage_index.append(attr_usage_index)
            
            if not attributes:
                attributes.append([1, size])
            else:
                attributes[0][0] += 1
                attributes[0][1] += size

        if attribute_exists(mesh_dict["uvs"]):
             for i in range(len(mesh_dict["uvs"][0])): # Just take first vertex's uv data [uv0, uv1, etc], as all vertices will have same number of uv channels
                add(15, 5, i, 4)

        if attribute_exists(mesh_dict["tangents"]):
            add(16, 6, 0, 8)

        if attribute_exists(mesh_dict["positions"]):
            add(10, 0, 0, 8)

        if attribute_exists(mesh_dict["normals"]):
            add(16, 3, 0, 8)

        if attribute_exists(mesh_dict["colors"]):
            for i in range(len(mesh_dict["colors"][0])): # Just take first vertex's color data [color0, color1, etc], as all vertices will have same number of color channels
                add(4, 10, i, 4)

        if BonePaletteCount:
            add(8, 1, 0, 4) # Blend Weights
            add(5, 2, 0, 4) # Blend Indices

        if attribute_exists(mesh_dict["binormals"]):
            add(16, 7, 0, 8)

        return {
            "attributes": attributes,
            "offset": offset,
            "type": type_,
            "usage": usage,
            "usage_index": usage_index
        }
    
    
    def get_armature_object(obj):
        # Find the armature object for this mesh
        for mod in obj.modifiers:
            if mod.type == 'ARMATURE':
                return mod.object
        return None
        
        
    def build_bone_palette(obj, armature_obj):
        if armature_obj is None:
            return {
                "bone_palette": [],
                "bone_mapping": {}
            }

        mesh = obj.to_mesh()

        # 1. Collect used vertex groups
        used_groups = {
            g.group
            for vert in mesh.vertices
            for g in vert.groups
        }

        # 2. Build (bone_index, vg_index) pairs
        pairs = []

        for vg_index in used_groups:
            vg = obj.vertex_groups[vg_index]

            bone_index = armature_obj.data.bones.find(vg.name)
            if bone_index == -1:
                continue

            pairs.append((bone_index, vg_index))

        # 3. SORT BY BONE INDEX (this gives ascending palette)
        pairs.sort(key=lambda x: x[0])

        # 4. Build final palette + mapping
        palette = []
        mapping = {}

        for bone_index, vg_index in pairs:
            mapping[vg_index] = len(palette)  # NEW compact index
            palette.append(bone_index)

        return {
            "bone_palette": palette,
            "bone_mapping": mapping
        }
    
    def clean_name(name):
        return name.rsplit(".", 1)[0]
        
    def get_material_name(obj):
        mats = obj.data.materials

        if mats and mats[0]:
            return clean_name(mats[0].name)

        return None

    
        
        

    # =========================
    # 2. COLLECT + PROCESS DATA
    # =========================

    mesh_data_list = []
    all_positions = []

    for obj in mesh_objects:
        armature_obj = get_armature_object(obj)
        bone_data = build_bone_palette(obj, armature_obj)
        BonePaletteCount = len(bone_data["bone_palette"])
        
        blender_mesh = BlenderMeshExtractor(obj, bone_data["bone_mapping"])
        mesh_dict = blender_mesh.ExtractBlenderMeshData()

        positions = mesh_dict["positions"]
        if not positions:
            continue
        
        all_positions.extend(positions)
        
        
        skeleton_name = armature_obj.name if armature_obj else None
        material_name = get_material_name(obj)
        
        mesh_data = {
            "obj": obj,
            "mesh": blender_mesh,
            "data": mesh_dict,
            "bounds": compute_bounds(positions),
            "attributes": build_attributes(mesh_dict, BonePaletteCount),
            "bone_data": bone_data,
            "vertex_count": len(blender_mesh.vertex_map),
            "triangles": mesh_dict["triangle_list"],
            "skeleton_name": skeleton_name,
            "material_name": material_name
        }

        mesh_data_list.append(mesh_data)

    # =========================
    # 3. MODEL-LEVEL DATA
    # =========================

    model_bounds = compute_bounds(all_positions)
    
    
    
    
    # Return all
    return {
    "meshes": mesh_data_list,
    "model_bounds": model_bounds
}


def get_bone_palette_count(blend_indices, blend_weights):
    used = set()

    for indices, weights in zip(blend_indices, blend_weights):
        for i, w in zip(indices, weights):
            if w > 0:
                used.add(i)

    return len(used)


    
    
# -----------------------------
# CONFIG (change for your engine)
# -----------------------------
FORWARD_AXIS = "Y"  # "Y" or "Z"
UP_VECTOR = Vector((0, 0, 1))
    
def build_bone_matrix(head: Vector, tail: Vector, roll: float) -> Matrix:
    
    # 1. Forward axis (bone direction)
    forward = (tail - head).normalized()

    # 2. Choose stable up reference
    world_up = UP_VECTOR.copy()

    if abs(forward.dot(world_up)) > 0.99:
        world_up = Vector((0, 1, 0))

    # 3. Right vector
    right = forward.cross(world_up).normalized()

    # 4. Recompute true up
    up = right.cross(forward).normalized()

    # 5. Apply roll around forward axis
    roll_mat = Matrix.Rotation(roll, 3, forward)
    right = roll_mat @ right
    up = roll_mat @ up

    # 6. Build matrix (DEFAULT: Y-forward engine style)
    if FORWARD_AXIS == "Y":
        M = Matrix((
            (right.x, forward.x, up.x, head.x),
            (right.y, forward.y, up.y, head.y),
            (right.z, forward.z, up.z, head.z),
            (0.0,     0.0,      0.0,   1.0)
        ))

    # Z-forward engine style (Unreal-like)
    elif FORWARD_AXIS == "Z":
        M = Matrix((
            (right.x, up.x, forward.x, head.x),
            (right.y, up.y, forward.y, head.y),
            (right.z, up.z, forward.z, head.z),
            (0.0,     0.0,   0.0,      1.0)
        ))

    else:
        raise ValueError("Invalid FORWARD_AXIS")

    return M
    
    
def remove_scale(m):
    c0 = Vector((m[0][0], m[1][0], m[2][0]))
    c1 = Vector((m[0][1], m[1][1], m[2][1]))
    c2 = Vector((m[0][2], m[1][2], m[2][2]))

    s0 = c0.length
    s1 = c1.length
    s2 = c2.length

    c0 /= s0
    c1 /= s1
    c2 /= s2

    return Matrix((
        (c0.x, c1.x, c2.x, m[3][0]),
        (c0.y, c1.y, c2.y, m[3][1]),
        (c0.z, c1.z, c2.z, m[3][2]),
        (0,0,0,1)
    ))
    
    
    
def get_global_bone_matrix(bone, armature):
    M = bone.matrix_local.copy()

    p = bone.parent
    while p:
        M = p.matrix_local @ M
        p = p.parent

    return armature.matrix_world @ M
    
    


