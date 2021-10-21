import bpy

def find_bsdf(mat):
    n_bsdf = None
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n_bsdf = n

    return n_bsdf


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

    n_bsdf.inputs[7].default_value = 0.9



