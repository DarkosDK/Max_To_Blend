bl_info = {
    "name": "Import From Max",
    "author": "DarkosDK",
    "version": (0, 1),
    "blender": (2, 90, 0),
    "category": "",
    "location": "View3D > Sidebar > Edit Tab",
    "description": "Import models from 3ds Max and convert/apply materials",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
}

import bpy
import os
import configparser
import codecs
from .utility import settings


def getModelIniFile(file_path, file_name):
    folder_name = '_' + file_name + '_import'
    fPath = os.path.join(file_path, folder_name, (file_name + '.ini'))

    return fPath

# iniFileName = 'm2b.ini'
# iniFolder = 'm2b_materials'
# userPath = os.path.expanduser('~')

# iniPath = os.path.join(userPath, iniFolder)
# ini = os.path.join(iniPath, iniFileName)

# if not os.path.exists(iniPath):
#     os.mkdir(iniPath)
#     open(ini, 'w').close()

ini = settings.ini
settings.initialize()


# List
class ListItem(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""

    name: bpy.props.StringProperty(
           name="Model Name",
           description="A name for this item",
           default="Untitled")

    model_path: bpy.props.StringProperty(
           name="Model Path",
           description="",
           default="")

class MY_UL_List(bpy.types.UIList):
    """Demo UIList."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

# Operators
class LIST_OT_NewItem(bpy.types.Operator):
    """Add a new item to the list."""

    bl_idname = "my_list.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        item = context.scene.my_list.add()
        item.name = 'New Item'

        return{'FINISHED'}

class LIST_OT_DeleteItem(bpy.types.Operator):
    """Delete the selected item from the list."""

    bl_idname = "my_list.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(cls, context):
        return context.scene.my_list

    def execute(self, context):
        my_list = context.scene.my_list
        index = context.scene.list_index

        my_list.remove(index)
        context.scene.list_index = min(max(0, index - 1), len(my_list) - 1)

        return{'FINISHED'}

class LIST_OT_PrintInfo(bpy.types.Operator):
    """Print some test info"""

    bl_idname = "my_list.print_info"
    bl_label = "Print Info"

    @classmethod
    def poll(cls, context):
        return context.scene.my_list

    def execute(self, context):
        my_list = context.scene.my_list
        index = context.scene.list_index
        item = my_list[index]

        model_ini_file = getModelIniFile(item.model_path, item.name)

        parser = settings.read_ini(model_ini_file)

        if ('Materials' in parser):
            for key in parser['Materials']: 
                print(key)

            black_mat = dict()
            settings.fill_dict(black_mat, parser, 'black')


            print(black_mat)
            return{'FINISHED'}
        else:
            return{'CANCELLED'}


        # a = ''

        # with open(ini, encoding="utf8", errors='ignore') as f:
        #     a = f.read()

        # config.read(a)

        # print(a)
        # print(config.sections())

        # parser = configparser.SafeConfigParser()
        # with codecs.open(ini, 'r', encoding='utf-16') as f:
        #     parser.readfp(f)

        # if ('Models' in parser):
        #     for key in parser['Models']: 
        #         item = context.scene.my_list.add()
        #         item.name = key
        #         item.model_path = parser['Models'][key]

        return{'FINISHED'}

class LIST_OT_ListUpdate(bpy.types.Operator):
    """Update imported models"""

    bl_idname = "my_list.update_list"
    bl_label = "Update"

    def execute(self, context):

        my_list = context.scene.my_list
        parser = configparser.SafeConfigParser()
        with codecs.open(ini, 'r', encoding='utf-16') as f:
            parser.readfp(f)

        my_list.clear()
        if ('Models' in parser):
            for key in parser['Models']: 
                item = context.scene.my_list.add()
                item.name = key
                item.model_path = parser['Models'][key]

        return{'FINISHED'}

class LIST_OT_ImportModels(bpy.types.Operator):
    """Import models from FBX file"""

    bl_idname = "my_list.import_model"
    bl_label = "Import model"

    @classmethod
    def poll(cls, context):
        return context.scene.my_list

    def execute(self, context):
        my_list = context.scene.my_list
        index = context.scene.list_index

        print(os.path.normpath(my_list[index].model_path))
        return{'FINISHED'}

# Panels
class DK_PT_Import_From_Max(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Check"
    bl_label = "Import From Max"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator('my_list.update_list', text='Update')
        row = layout.row()
        row.template_list("MY_UL_List", "The_List", context.scene, "my_list", context.scene, "list_index")

        col.label(text='Models List')

        row = layout.row()
        row.operator('my_list.import_model', text='Import Model')
        row.operator('my_list.print_info', text='Info')
        # row.operator('my_list.new_item', text='New')
        # row.operator('my_list.delete_item', text='Delete')
        # row.operator('my_list.print_info', text='Info')

blender_classes = [  
    DK_PT_Import_From_Max,
    MY_UL_List,
    LIST_OT_NewItem,
    LIST_OT_DeleteItem,
    LIST_OT_PrintInfo,
    LIST_OT_ListUpdate,
    LIST_OT_ImportModels,
]

def register():
    bpy.utils.register_class(ListItem)
    bpy.types.Scene.my_list = bpy.props.CollectionProperty(type = ListItem)
    bpy.types.Scene.list_index = bpy.props.IntProperty(name = "Index for my_list", default = 0)
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)

def unregister():
    # Unregister classes
    for blender_class in reversed(blender_classes):
        bpy.utils.unregister_class(blender_class)
    bpy.utils.unregister_class(ListItem)
    # Unregister properties
    del bpy.types.Scene.list_index
    del bpy.types.Scene.my_list

if __name__ == "__main__":
    register()