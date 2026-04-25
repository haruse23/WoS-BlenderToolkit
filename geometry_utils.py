import bmesh

def make_triangle_strip(triangles, vertex_count):
    """Create a triangle strip from triangles, safe for Blender import with consistent winding."""
    if not triangles:
        return []

    strip = []
    last = None  # last two vertices in the strip

    for i, tri in enumerate(triangles):
        # Ensure indices are valid
        tri = [v for v in tri if 0 <= v < vertex_count]
        if len(tri) != 3:
            continue  # skip invalid triangle

        # Reverse winding for every odd triangle
        if i % 2 == 1:
            tri = [tri[0], tri[1], tri[2]]

        if i > 0:
            # Add degenerate to restart strip
            strip.append(strip[-1])
            strip.append(tri[0])

        # Add the triangle vertices
        strip.extend(tri)
        last = tri[-2:]  # last two for next iteration

    return strip
    
    
def reverse_winding_order_export(indices):
    indices[1::3], indices[2::3] = indices[2::3], indices[1::3]
    return indices

def reverse_winding_order_import(triangles):
    return [(tri[0], tri[2], tri[1]) for tri in triangles]
    
def flip_uv_v_axis(bm):
    uv_layers = bm.loops.layers.uv
    if not uv_layers:
        return
    
    for uv_layer in uv_layers:
        for face in bm.faces:
            for loop in face.loops:

                uv = loop[uv_layer]

                u, v = uv.uv.x, uv.uv.y

                uv.uv.x = u
                uv.uv.y = 1.0 - v