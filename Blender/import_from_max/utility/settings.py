import os
import configparser
import codecs

iniFileName = 'm2b.ini'
iniFolder = 'm2b_materials'
userPath = os.path.expanduser('~')

iniPath = os.path.join(userPath, iniFolder)

# Main INI File
ini = os.path.join(iniPath, iniFileName)

def initialize():
    if not os.path.exists(iniPath):
        os.mkdir(iniPath)
        open(ini, 'w').close()

def read_ini(ini_path):
    parser = configparser.SafeConfigParser()
    with codecs.open(ini_path, 'r', encoding='utf-16') as f:
        parser.readfp(f)

    return parser

def fill_dict(dict_to_write, ini_file, section_name):
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


def collect_material_settings(ini_path):
    material_settings = dict()

    parser = read_ini(ini_path)


    return material_settings