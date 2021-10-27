from .settings import ini
import bpy
import os
import shutil
import configparser
import codecs

# ini = settings.ini

def create_import_folder(model_name, model_path):
    folder_name = '_' + model_name + '_import'
    return os.path.join(model_path, folder_name)

def create_fbx_path(model_name, model_path):
    fbx_folder = create_import_folder(model_name, model_path)
    return os.path.join(fbx_folder, (model_name + '.fbx'))

def remove_model_from_list(model_name, model_path):
    # Delete folder with fbx and model ini
    folder_to_del = create_import_folder(model_name, model_path)
    if os.path.exists(folder_to_del):
        shutil.rmtree(folder_to_del)

    # Remove model's info from global ini file
    parser = configparser.SafeConfigParser()
    with codecs.open(ini, 'r', encoding='utf-16') as f:
        parser.readfp(f)
    if ('Models' in parser):
        if model_name in parser['Models']: 
            parser.remove_option('Models', model_name)
            with codecs.open(ini, 'w', encoding='utf-16') as configfile:
                parser.write(configfile)

def fix_materials():
    main_materials = []
    dupli_materials = []
    for mat in bpy.data.materials:
        ind = mat.name.find('.')
        if ind != -1:
            dupli_materials.append(mat)
        else:
            main_materials.append(mat)

    for mat in dupli_materials:
        main_name = mat.name[:(mat.name.find('.'))]
        for i in main_materials:
            if i.name == main_name:
                mat.user_remap(i)

    # Delete unused materials
    for i in dupli_materials:
        if i.users == 0:
            bpy.data.materials.remove(i)