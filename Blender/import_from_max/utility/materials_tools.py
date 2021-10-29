import bpy

def find_bsdf(mat):
    n_bsdf = None
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n_bsdf = n

    return n_bsdf

def find_node_position(node, input_ind):
    deltaY = 0
    if node.type == 'BSDF_PRINCIPLED':
        deltaY = 100
    input_deltaY = 20 * input_ind
    deltaY += input_deltaY
    deltaX = 300

    return (node.location.x - deltaX, node.location.y - deltaY)

def create_mix_node(mat, node, input_ind: int):

    # Find new node position 
    n_mix_location = find_node_position(node, input_ind)

    # Create node
    n_mix = mat.node_tree.nodes.new('ShaderNodeMixRGB')
    n_mix.location = n_mix_location
    mat.node_tree.links.new(n_mix.outputs[0], node.inputs[input_ind])

    return n_mix


def set_texture(mat, node, input_ind: int, texture_path: str, isSRGB: bool, mult, init_color=(1.0, 1.0, 1.0, 1.0)):
    link = mat.node_tree.links.new

    node_to_link = node
    index_to_link = input_ind

    if mult != 1.0:
        n_mix = create_mix_node(mat, node, 0)
        n_mix.inputs[1].default_value = init_color
        n_mix.inputs[0].default_value = mult
        node_to_link = n_mix
        index_to_link = 2

    # Find new node position 
    n_texture_map_location = find_node_position(node_to_link, index_to_link)
    
    # Texture node
    n_texture_map = mat.node_tree.nodes.new('ShaderNodeTexImage')
    n_texture_map.location = n_texture_map_location
    new_img = bpy.data.images.load(filepath = texture_path)
    n_texture_map.image = new_img
    # For test
    if isSRGB:
        new_img.colorspace_settings.name = 'sRGB'
    else:
        new_img.colorspace_settings.name = 'Non-Color'
    link(n_texture_map.outputs[0], node_to_link.inputs[index_to_link])

    # Mapping node
    n_mapping = mat.node_tree.nodes.new('ShaderNodeMapping')
    n_mapping.location = (n_texture_map.location.x - 220, n_texture_map.location.y)
    link(n_mapping.outputs[0], n_texture_map.inputs[0])

    # Text_coords node
    n_texture_coord = mat.node_tree.nodes.new('ShaderNodeTexCoord')
    n_texture_coord.location = (n_mapping.location.x - 220, n_mapping.location.y)
    link(n_texture_coord.outputs[2], n_mapping.inputs[0])

def create_map(mat, node, input_ind: int):
    pass

class BSDF():
    def __init__(self, material) -> None:
        self.mat = material
        self.bsdf_node = find_bsdf(self.mat)
        self.diff_color = None

    def set_diffuse(self, color):
        self.bsdf_node.inputs[0].default_value = color
        self.diff_color = color
    
    def set_diffuse_texture(self, text_path, mult):
        set_texture(self.mat, self.bsdf_node, 0, text_path, True, mult, self.diff_color)
        # if mult == 1.0:
        #     set_texture(self.mat, self.bsdf_node, 0, text_path, True)
        # else:
        #     n_mix = create_mix_node(self.mat, self.bsdf_node, 0)
        #     if self.diff_color is not None:
        #         n_mix.inputs[1].default_value = self.diff_color
        #     n_mix.inputs[0].default_value = mult
        #     set_texture(self.mat, n_mix, 2, text_path, True)

    def set_spec_texture(self, text_path):
        pass
        # set_texture(self.mat, self.bsdf_node, 5, text_path, False)

    def set_specular(self, value):
        self.bsdf_node.inputs[5].default_value = value

    def set_roughness(self, value):
        self.bsdf_node.inputs[7].default_value = value

    def set_roughness_texture(self, text_path):

        # Invert node
        n_invert_position = find_node_position(self.bsdf_node, 7)

        n_invert = self.mat.node_tree.nodes.new('ShaderNodeInvert')
        n_invert.location = n_invert_position
        self.mat.node_tree.links.new(n_invert.outputs[0], self.bsdf_node.inputs[7])

        # set_texture(self.mat, n_invert, 0, text_path, False)



# Delete all nodes in material and create setup with Principled BSDF and Output nodes
def clean_material_nodes(mat):
    mat.use_nodes = True
    
    # Clean nodes
    n_out = None
    for n in mat.node_tree.nodes:
        if n.type != 'OUTPUT_MATERIAL':
            mat.node_tree.nodes.remove(n)
        else:
            n_out = n
            
    n_out.location = (400, 0)
    # Create Principled BSDF node
    n_bsdf = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    
    link = mat.node_tree.links.new
    link(n_bsdf.outputs[0], n_out.inputs[0])

# Clean all nodes in all materials in object's material slots
def clean_object_materials(ob):
    materials_count = len(ob.material_slots.values())

    for i in range(0, materials_count):
        ob.active_material_index = i
        mat = ob.active_material
        clean_material_nodes(mat)

# Create a Carpaint material
def create_carpaint_material_metal(mat, color):
    clean_material_nodes(mat)
    link = mat.node_tree.links.new

    # Get BSDF Node
    n_bsdf = None
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n_bsdf = n

    # Set main color
    #n_bsdf = bpy.types.Node  # REMOVE, JUST FOR AUTOCOMPLITION
    n_bsdf.inputs[0].default_value = color

    # Set metallness
    n_bsdf.inputs[4].default_value = 1.0    

    # Set Specular
    n_bsdf.inputs[5].default_value = 0.2

    # Set Roughness
    n_bsdf.inputs[7].default_value = 0.3

    # Set Clearcoat
    n_bsdf.inputs[12].default_value = 2.0

    # Set Clearcoat Roughness
    n_bsdf.inputs[13].default_value = 0.03

    # Create Normal Map Setup
    n_normal_map = mat.node_tree.nodes.new('ShaderNodeNormalMap')
    n_normal_map.location = (-300, -300)
    n_normal_map.inputs[0].default_value = 0.03
    link(n_normal_map.outputs[0], n_bsdf.inputs[20])

    n_combine_rgb = mat.node_tree.nodes.new('ShaderNodeCombineRGB')
    n_combine_rgb.location = (-500, -400)
    n_combine_rgb.inputs[2].default_value = 0.0
    link(n_combine_rgb.outputs[0], n_normal_map.inputs[1])

    n_separate_rgb = mat.node_tree.nodes.new('ShaderNodeSeparateRGB')
    n_separate_rgb.location = (-700, -400)
    link(n_separate_rgb.outputs[0], n_combine_rgb.inputs[0])
    link(n_separate_rgb.outputs[1], n_combine_rgb.inputs[1])

    n_voronoi_texture = mat.node_tree.nodes.new('ShaderNodeTexVoronoi')
    n_voronoi_texture.location = (-940, -300)
    link(n_voronoi_texture.outputs[1], n_separate_rgb.inputs[0])
    n_voronoi_texture.inputs[2].default_value = 5.0
    n_voronoi_texture.inputs[5].default_value = 1.0

    n_mapping_01 = mat.node_tree.nodes.new('ShaderNodeMapping')
    n_mapping_01.location = (-1300, -300)
    link(n_mapping_01.outputs[0], n_voronoi_texture.inputs[0])

    n_value_01 = mat.node_tree.nodes.new('ShaderNodeValue')
    n_value_01.location = (-1500, -530)
    n_value_01.outputs[0].default_value = 1500.0
    link(n_value_01.outputs[0], n_mapping_01.inputs[3])

    # Create ClearCoat Normal Setup
    n_bump = mat.node_tree.nodes.new('ShaderNodeBump')
    n_bump.location = (-300, -600)
    n_bump.inputs[0].default_value = 0.7
    n_bump.inputs[1].default_value = 0.00001
    link(n_bump.outputs[0], n_bsdf.inputs[21])

    n_noise = mat.node_tree.nodes.new('ShaderNodeTexNoise')
    n_noise.location = (-600, -600)
    n_noise.inputs[2].default_value = 5.0
    n_noise.inputs[3].default_value = 0.0
    n_noise.inputs[4].default_value = 0.5
    n_noise.inputs[5].default_value = 0.0
    link(n_noise.outputs[0], n_bump.inputs[2])

    n_mapping_02 = mat.node_tree.nodes.new('ShaderNodeMapping')
    n_mapping_02.location = (-1000, -600)
    link(n_mapping_02.outputs[0], n_noise.inputs[0])

    n_value_02 = mat.node_tree.nodes.new('ShaderNodeValue')
    n_value_02.location = (-1200, -840)
    n_value_02.outputs[0].default_value = 300.0
    link(n_value_02.outputs[0], n_mapping_02.inputs[3])

    # Add Texture Coordinate
    n_texture_coord = mat.node_tree.nodes.new('ShaderNodeTexCoord')
    n_texture_coord.location = (-1900, -600)
    link(n_texture_coord.outputs[3], n_mapping_01.inputs[0])
    link(n_texture_coord.outputs[3], n_mapping_02.inputs[0])

def create_carpaint_material_glossy(mat, color):
    create_carpaint_material_metal(mat, color)

    n_bsdf = find_bsdf(mat)

    n_bsdf.inputs[4].default_value = 0.0
    n_bsdf.inputs[7].default_value = 0.35

def parse_color(str_color: str):
    # Remove brackets
    str_color = str_color[1:len(str_color) - 1]
    # Return Color value from string description
    elements = str_color.rsplit(' ')
    color = (float(elements[1])/255, float(elements[2])/255, float(elements[3])/255, 1)
    return color

def create_custom_mat(mat, description: dict):
    clean_material_nodes(mat)
    link = mat.node_tree.links.new

    bsdf = BSDF(mat)

    # DIFFUSE
    if 'diffuse_color' in description.keys():
        bsdf.set_diffuse(parse_color(description['diffuse_color']))

        if 'texmap_diffuse' in description.keys():
            if description['texmap_diffuse'] != 'undefined' and type(description['texmap_diffuse']) == dict:
                if description['texmap_diffuse']['_type'] == 'bitmaptexture':
                    # Mix texture with color
                    if 'texmap_diffuse_multiplier' in description.keys():
                        diff_mult = (float(description['texmap_diffuse_multiplier']))/100.0
                        bsdf.set_diffuse_texture(description['texmap_diffuse']['texture'], diff_mult)               


    # Reflection
    if 'reflection_color' in description.keys():
        spec_color = parse_color(description['reflection_color'])
        spec_value = max([spec_color[0], spec_color[1], spec_color[2]])
        bsdf.set_specular(spec_value)

    if 'texmap_reflection' in description.keys():
        if description['texmap_reflection'] != 'undefined' and type(description['texmap_reflection']) == dict:
            if description['texmap_reflection']['_type'] == 'bitmaptexture':
                bsdf.set_spec_texture(description['texmap_reflection']['texture'])

    # Roughness
    if 'reflection_glossiness' in description.keys():
        glossy_value = float(description['reflection_glossiness'])
        bsdf.set_roughness(1 - glossy_value)

    if 'texmap_reflectionglossiness' in description.keys():
        if description['texmap_reflectionglossiness'] != 'undefined' and type(description['texmap_reflectionglossiness']) == dict:
            if description['texmap_reflectionglossiness']['_type'] == 'bitmaptexture':
                bsdf.set_roughness_texture(description['texmap_reflectionglossiness']['texture'])


        
    
