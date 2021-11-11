import os
import configparser
import codecs

iniFileName = 'm2b.ini'
iniFolder = 'm2b_materials'
userPath = os.path.expanduser('~')

iniPath = os.path.join(userPath, iniFolder)

# Main INI File
ini = os.path.join(iniPath, iniFileName)

used_materials = [
    'VRayMtl',
]


def initialize():
    if not os.path.exists(iniPath):
        os.mkdir(iniPath)
        open(ini, 'w').close()

def read_ini(ini_path):
    parser = configparser.SafeConfigParser()
    with codecs.open(ini_path, 'r', encoding='utf-8') as f:
        parser.readfp(f)

    return parser

def fill_dict(dict_to_write, ini_file, section_name):
    if section_name in ini_file.sections():
        section = ini_file[section_name]
        for i in section:
            value = section[i]
            if value.find('inner_attachment:') == -1:
                dict_to_write[i] = section[i]
            else:
                new_dict = dict()
                new_path = os.path.join(section_name, i)
                dict_to_write[i] = fill_dict(new_dict, ini_file, (section_name + '\\\\' + i))
    
    return dict_to_write

def create_dict_all_materials(ini_file):
    global_dict = dict()
    if ('Materials' in ini_file):
        for key in ini_file['Materials']: 
            # if ini_file['Materials'][key] in used_materials:
            mat_dict = dict()
            fill_dict(mat_dict, ini_file, key)
            global_dict[key] = mat_dict
    return global_dict

def collect_material_settings(ini_path):
    material_settings = dict()

    parser = read_ini(ini_path)


    return material_settings