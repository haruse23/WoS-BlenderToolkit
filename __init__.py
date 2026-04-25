import bpy
import bpy.utils.previews as previews
from bpy.types import Operator, FileHandler, PropertyGroup, Menu, Panel
from bpy.props import StringProperty, BoolProperty, CollectionProperty, IntProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper, orientation_helper, axis_conversion
import os

from .BlenderImport import *
from .BlenderExport import *
from .rename_vertex_groups import *

from .Convert import *

import bmesh

bl_info = {
    "name": "WoS BlenderToolkit",
    "author": "haru233",
    "version": (1, 0, 2),
    "blender": (4, 5, 0),
    "location": "File --> Import, File --> Export, Drag-and-Drop (Import/Convert)",
    "description": "Blender addon/plugin for the video game Spider-Man: Web of Shadows"
}



class ExportCollectionItem(PropertyGroup):
    name: StringProperty()
    export: BoolProperty(name="Export", default=True)


def init_collection_properties():
    bpy.types.Scene.export_collections = CollectionProperty(type=ExportCollectionItem)
    bpy.types.Scene.export_collections_index = IntProperty(default=0)

def populate_collections():
    scene = bpy.context.scene
    scene.export_collections.clear()
    for col in bpy.data.collections:
        item = scene.export_collections.add()
        item.name = col.name
        item.export = True

# Model
# ------------------------------
class IMPORT_OT_Mesh_File_View(Operator):
    bl_idname = "import_scene.smwos_mesh_importer_file_view"
    bl_label = "Import Wrap Mesh File (WOS)"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".mesh"
    
    filter_glob: StringProperty(default="*.mesh", options={'HIDDEN'},)
    
    # Filepath property
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)
    directory: StringProperty(subtype="DIR_PATH")
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.label(text="Import Options")
        layout.prop(scene, "flip_uv_v_avis")
        layout.prop(scene, "reverse_winding_order")
        layout.prop(scene, "convert_to_triangle_list")
             
    def execute(self, context):
        if not self.files:
            self.report({'WARNING'}, "No files received")
            return {'CANCELLED'}

        for file in self.files:
            filepath = os.path.join(self.directory, file.name)

            try:
                
                ImportModel(filepath)
            except Exception as e:
                self.report({'ERROR'}, f"{file.name}: {e}")
            
        self.report({'INFO'}, f"Imported {len(self.files)} file(s)")
        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}


class IMPORT_OT_Mesh_Drag_and_Drop(Operator):
    bl_idname = "import_scene.smwos_mesh_importer_drag_and_drop"
    bl_label = "Import Wrap Mesh File (WOS)"
    bl_options = {'REGISTER', 'UNDO'}

    # Filepath property
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        if not self.files:
            self.report({'WARNING'}, "No files received")
            return {'CANCELLED'}

        for file in self.files:
            filepath = os.path.join(self.directory, file.name)

            try:
                
                ImportModel(filepath)
            except Exception as e:
                self.report({'ERROR'}, f"{file.name}: {e}")

        self.report({'INFO'}, f"Imported {len(self.files)} file(s)")
        return {'FINISHED'}
    


class Mesh_FileHandler(FileHandler):
    bl_idname = "MESH_FILEHANDLER"
    bl_label = "Import Wrap Mesh File (WOS)"
    bl_import_operator = "import_scene.smwos_mesh_importer_drag_and_drop"
    bl_file_extensions = ".mesh"
    
    @classmethod
    def poll_drop(cls, context):
        return context.area and context.area.type == "VIEW_3D"


class EXPORT_OT_Mesh(Operator, ExportHelper):
    bl_idname = "export_scene.smwos_mesh_exporter"
    bl_label = "Export Wrap Mesh File (WOS)"
    bl_options = {'PRESET'}
    
    filename_ext = ".mesh"
    
    filter_glob: StringProperty(default="*.mesh", options={'HIDDEN'},)
    
    def invoke(self, context, event):
        populate_collections()  # populate checkbox list
        return super().invoke(context, event)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.label(text="Collections:")
        for item in scene.export_collections:
            
            layout.prop(item, "export", text=item.name)
            
        layout.separator()
        layout.label(text="Export Options")
        layout.prop(scene, "flip_uv_v_avis")
        layout.prop(scene, "reverse_winding_order")

    def execute(self, context):
        scene = context.scene
        base_dir = os.path.dirname(self.filepath)
        filename = os.path.basename(self.filepath)
        name, ext = os.path.splitext(filename)

        exported_count = 0
        for item in scene.export_collections:
            if item.export:
                collection = bpy.data.collections.get(item.name)
                
                # Hash prepended filename
                hash_int = Hash(collection.name)
                hash_str = f"{hash_int & 0xFFFFFFFF:X}"
                collection_file = os.path.join(base_dir, f"0x{hash_str}.{collection.name}.wrap{ext}")
                
                depsgraph = bpy.context.evaluated_depsgraph_get()
                mesh_objects = [obj.evaluated_get(depsgraph) for obj in collection.objects if obj.type == "MESH"]
                
                # Export each collection to its own file
                ExportModel(collection, collection_file, mesh_objects)
                exported_count += 1

        self.report({'INFO'}, f"Exported {exported_count} collections")
        return {'FINISHED'}
    

# Skeleton
# -------------------------------
class IMPORT_OT_Skeleton_File_View(Operator):
    bl_idname = "import_scene.smwos_skeleton_importer_file_view"
    bl_label = "Import Wrap Skeleton File (WOS)"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".skel"
    
    filter_glob: StringProperty(default="*.skel", options={'HIDDEN'},)
    
    # Filepath property
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)
    directory: StringProperty(subtype="DIR_PATH")
    
    def execute(self, context):
        if not self.files:
            self.report({'WARNING'}, "No files received")
            return {'CANCELLED'}

        for file in self.files:
            filepath = os.path.join(self.directory, file.name)

            try:
                ImportSkeleton(filepath)
            except Exception as e:
                self.report({'ERROR'}, f"{file.name}: {e}")

        self.report({'INFO'}, f"Imported {len(self.files)} file(s)")
        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}
        
class IMPORT_OT_Skeleton_Drag_and_Drop(Operator):
    bl_idname = "import_scene.smwos_skeleton_importer_drag_and_drop"
    bl_label = "Import Wrap Skeleton File (WOS)"
    bl_options = {'REGISTER', 'UNDO'}

    # Filepath property
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        if not self.files:
            self.report({'WARNING'}, "No files received")
            return {'CANCELLED'}

        for file in self.files:
            filepath = os.path.join(self.directory, file.name)

            try:
                ImportSkeleton(filepath)
            except Exception as e:
                self.report({'ERROR'}, f"{file.name}: {e}")

        self.report({'INFO'}, f"Imported {len(self.files)} file(s)")
        return {'FINISHED'}
    


class Skeleton_FileHandler(FileHandler):
    bl_idname = "SKELETON_FILEHANDLER"
    bl_label = "Import Wrap Skeleton File (WOS)"
    bl_import_operator = "import_scene.smwos_skeleton_importer_drag_and_drop"
    bl_file_extensions = ".skel"
    
    @classmethod
    def poll_drop(cls, context):
        return context.area and context.area.type == "VIEW_3D"






class EXPORT_OT_Skeleton(Operator, ExportHelper):
    bl_idname = "export_scene.smwos_skeleton_exporter"
    bl_label = "Export Wrap Skeleton File (WOS)"
    bl_options = {'PRESET'}
    
    filename_ext = ".skel"
    
    filter_glob: StringProperty(default="*.skel", options={'HIDDEN'},)
    
    def execute(self, context):
        scene = context.scene
        
        Armatures = [obj for obj in context.selected_objects if obj.type == "ARMATURE"]
        
        armature_count = 0
        
        for Armature in Armatures:   
            base_dir = os.path.dirname(self.filepath)
            filename = os.path.basename(self.filepath)
            name, ext = os.path.splitext(filename)
            
            skeleton_name = Armature.name
            
            # Hash prepended filename
            hash_int = Hash(skeleton_name)
            hash_str = f"{hash_int & 0xFFFFFFFF:X}"
            skeleton_filepath = os.path.join(base_dir, f"0x{hash_str}.{skeleton_name}.wrap{ext}")

            
            ExportSkeleton(skeleton_filepath, Armature)
            armature_count += 1

        self.report({'INFO'}, f"Exported {armature_count} WOS Wrapped Skeleton File(s)")
        return {'FINISHED'}



# Rename Vertex Groups feature
# -------------------------------------
def get_collections(self, context):
    items = []

    for col in context.scene.collection.children:
        items.append((col.name, col.name, ""))

    return items
    

class MYADDON_OT_Rename_Vertex_Groups(Operator):
    bl_idname = "myaddon.rename_vertex_groups"
    bl_label = "Rename Vertex Groups"

    def execute(self, context):
        collection = context.scene.collection_search_dropdown
        
        if collection:
            Rename_Vertex_Groups(collection)
        
        return {'FINISHED'}
        
        
class MYADDON_PT_panel(Panel):
    bl_label = "WOS Tools"          # Title
    bl_idname = "MYADDON_PT_panel"
    bl_space_type = 'VIEW_3D'      # 3D viewport
    bl_region_type = 'UI'          # Side panel (N panel)
    bl_category = "WOS Tools"         # Tab name (right side)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.label(text="Rename Vertex Groups")
        layout.label(text="Collections:")
        layout.prop_search(scene, "collection_search_dropdown", bpy.data, "collections", text="")
        layout.operator("myaddon.rename_vertex_groups", text="Rename Vertex Groups")
        
        






# Menu
# ---------------
class IMPORT_MT_WoS(Menu):
    bl_label = "WOS Blender Addon"
    bl_idname = "IMPORT_MT_wos_blender_addon"
    
    def draw(self, context):
        self.layout.operator(IMPORT_OT_Mesh_File_View.bl_idname, text="Wrapped Model (WOS)", icon="MESH_DATA")
        self.layout.operator(IMPORT_OT_Skeleton_File_View.bl_idname, text="Wrapped Skeleton (WOS)", icon="ARMATURE_DATA")
        

class EXPORT_MT_WoS(Menu):
    bl_label = "WOS Blender Addon"
    bl_idname = "EXPORT_MT_wos_blender_addon"
    
    def draw(self, context):
        self.layout.operator(EXPORT_OT_Mesh.bl_idname, text="Wrapped Model (WOS)", icon="MESH_DATA")
        self.layout.operator(EXPORT_OT_Skeleton.bl_idname, text="Wrapped Skeleton (WOS)", icon="ARMATURE_DATA")


# Textures
# --------------------------
class CONVERT_OT_DDS_TEX(Operator):
    """Drag and Drop DDS or TEX files to convert"""
    bl_idname = "import_scene.dds_tex_converter"
    bl_label = "DDS/TEX Converter (WOS)"
    bl_options = {'REGISTER', 'UNDO'}

    # Filepath property
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        if not self.files:
            self.report({'WARNING'}, "No files received")
            return {'CANCELLED'}

        for file in self.files:
            filepath = os.path.join(self.directory, file.name)

            try:
                Convert(filepath, DDS, TEX)
            except Exception as e:
                self.report({'ERROR'}, f"{file.name}: {e}")

        self.report({'INFO'}, f"Converted {len(self.files)} file(s)")
        return {'FINISHED'}
    


class DDS_TEX_FileHandler(FileHandler):
    bl_idname = "DDS_TEX_FILEHANDLER"
    bl_label = "Convert DDS/TEX Files (WOS)"
    bl_import_operator = "import_scene.dds_tex_converter"
    bl_file_extensions = ".dds;.tex"
    
    @classmethod
    def poll_drop(cls, context):
        return context.area and context.area.type == "VIEW_3D"
    
    @classmethod
    def can_handle(cls, context, filepath):
        return filepath.lower().endswith((".dds", ".tex"))
        
        
# Custom Icons
custom_icons = {}

def RegisterCustomIcon():
    pcoll = previews.new()
    script_path = os.path.dirname(__file__)
    icons_dir = os.path.join(script_path, "Icons")
    pcoll.load("wos_blendertoolkit_icon", os.path.join(icons_dir, "Icon.png"), 'IMAGE')
    custom_icons["main"] = pcoll


def UnregisterCustomIcon():
    for pcoll in custom_icons.values():
        previews.remove(pcoll)
    custom_icons.clear()
    
# Register the operator
def menu_func_import(self, context):
    my_icon = custom_icons["main"]["wos_blendertoolkit_icon"]
    self.layout.menu(IMPORT_MT_WoS.bl_idname, icon_value=my_icon.icon_id)
    
# Register the operator
def menu_func_export(self, context):
    my_icon = custom_icons["main"]["wos_blendertoolkit_icon"]
    self.layout.menu(EXPORT_MT_WoS.bl_idname, icon_value=my_icon.icon_id)
    


classes = (
    IMPORT_OT_Mesh_File_View,
    IMPORT_OT_Mesh_Drag_and_Drop,
    Mesh_FileHandler,
    ExportCollectionItem,
    EXPORT_OT_Mesh,
    IMPORT_MT_WoS,
    
    IMPORT_OT_Skeleton_File_View,
    IMPORT_OT_Skeleton_Drag_and_Drop,
    Skeleton_FileHandler,
    EXPORT_OT_Skeleton,
    EXPORT_MT_WoS,
    
    MYADDON_OT_Rename_Vertex_Groups,
    MYADDON_PT_panel,
    
    CONVERT_OT_DDS_TEX,
    DDS_TEX_FileHandler,
    
    
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    bpy.types.Scene.export_collections = bpy.props.CollectionProperty(type=ExportCollectionItem)
    bpy.types.Scene.export_collections_index = bpy.props.IntProperty(default=0)
    
    bpy.types.Scene.collection_search_dropdown = bpy.props.PointerProperty(
        type=bpy.types.Collection,
        name="Collections"
    )
    
    bpy.types.Scene.flip_uv_v_avis = bpy.props.BoolProperty(
        name="Flip UV V-Axis",
        default=False
    )
    
    bpy.types.Scene.reverse_winding_order = bpy.props.BoolProperty(
        name="Reverse Triangle Winding Order",
        default=False
    )
    
    bpy.types.Scene.convert_to_triangle_list = bpy.props.BoolProperty(
        name="Convert to Triangle List",
        default=False
    )
    
    RegisterCustomIcon()
    
   


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    if hasattr(bpy.types.Scene, "export_collections"):
        del bpy.types.Scene.export_collections

    if hasattr(bpy.types.Scene, "export_collections_index"):
        del bpy.types.Scene.export_collections_index
        
    if hasattr(bpy.types.Scene, "collection_search_dropdown"):
        del bpy.types.Scene.collection_search_dropdown
        
    if hasattr(bpy.types.Scene, "flip_uv_v_avis"):
        del bpy.types.Scene.flip_uv_v_avis
        
    if hasattr(bpy.types.Scene, "reverse_winding_order"):
        del bpy.types.Scene.reverse_winding_order
    
    if hasattr(bpy.types.Scene, "convert_to_triangle_list"):
        del bpy.types.Scene.convert_to_triangle_list

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
    
    UnregisterCustomIcon()

if __name__ == "__main__":
    register()
