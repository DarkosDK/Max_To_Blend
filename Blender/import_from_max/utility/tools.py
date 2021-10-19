import os

def create_import_folder(model_name, model_path):
    folder_name = '_' + model_name + '_import'
    return os.path.join(model_path, folder_name)

def create_fbx_path(model_name, model_path):
    fbx_folder = create_import_folder(model_name, model_path)
    return os.path.join(fbx_folder, (model_name + '.fbx'))