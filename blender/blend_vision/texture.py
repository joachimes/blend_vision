from audioop import mul
from platform import node
import bpy
import os
import random

class texture():
    def __init__(self, path:str) -> None:
        self.path = path
        self.obj_name_ext = '_material_dispalcement'


    def set_material(self, obj, texPath):
        base_name = self.extract_base_name(texPath)

        mat = None
        if base_name not in bpy.data.materials:
            mat = bpy.data.materials.new(name=base_name)
        else:
            mat = bpy.data.materials[base_name]
        mat.use_nodes = True
        
        mat.cycles.displacement_method = 'BOTH'

        # Get and set up nodes
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        mat_output = mat.node_tree.nodes["Material Output"]
        
        mapping = mat.node_tree.nodes.new('ShaderNodeMapping')
        # Change scale of texture map
        scale = random.gauss(100,20)
        mapping.inputs['Scale'].default_value[0] = scale
        mapping.inputs['Scale'].default_value[1] = scale
        tex_coord = mat.node_tree.nodes.new('ShaderNodeTexCoord')
        mat.node_tree.links.new(mapping.inputs['Vector'], tex_coord.outputs['UV'])

        # Read each img and connect tex to correct socket
        for path in os.listdir(texPath):
            tex_img_path = os.path.join(texPath, path)
            path_type = path[len(base_name):len(base_name)+3]
            if path_type == 'dis': # Displacement map
                self.add_geo_node_displacement(obj, tex_img_path, scale)
                continue
            new_img_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
            new_img_node.image = bpy.data.images.load(tex_img_path)
            mat.node_tree.links.new(new_img_node.inputs['Vector'], mapping.outputs['Vector'])
            node_output = new_img_node.outputs['Color']
            if path_type == 'dif': # Base Material
                mat.node_tree.links.new(bsdf.inputs['Base Color'], node_output)
            
            elif path_type == 'rou': # Roughness map
                mat.node_tree.links.new(bsdf.inputs['Roughness'], node_output)
            
            elif path_type == 'nor': # Normal map
                normal_node = mat.node_tree.nodes.new('ShaderNodeNormalMap')
                mat.node_tree.links.new(normal_node.inputs['Color'], node_output)
                mat.node_tree.links.new(bsdf.inputs['Normal'], normal_node.outputs['Normal'])
            
                
        # Assign it to object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)


    def extract_base_name(self, imgPath) -> str:
        base_name = ''
        for path in os.listdir(imgPath):
            if base_name == '':
                base_name = path
                continue
            iter_string = path
            # Remove end of string
            while iter_string not in base_name:
                iter_string = iter_string[:-1]
            base_name = iter_string
            
        return base_name


    def add_geo_node_displacement(self, obj, disp_map_path, tex_coord_scale, height_scale=2):
        modifier = None
        modifier_name = obj.name + self.obj_name_ext
        geo_node = [mod for mod in obj.modifiers if mod.type == 'NODES' and mod.name == modifier_name]
        if geo_node:
            modifier = geo_node[0]
            self.delete_geo_node(modifier_name)

        modifier = obj.modifiers.new(modifier_name, type='NODES')
        
        tree = modifier.node_group
        nodes = tree.nodes

        # Position node
        pos_node = nodes.new('GeometryNodeInputPosition')
        
        # Attribute stat node
        att_stat = nodes.new('GeometryNodeAttributeStatistic')
        att_stat.data_type = 'FLOAT_VECTOR'
        tree.links.new(att_stat.inputs['Geometry'], nodes['Group Input'].outputs['Geometry'])
        tree.links.new(att_stat.inputs['Attribute'], pos_node.outputs['Position'])

        # Vector math nodes: subtract, divide (Normalization)
        sub_math = nodes.new('ShaderNodeVectorMath')
        sub_math.operation = 'SUBTRACT'
        tree.links.new(sub_math.inputs[0], pos_node.outputs['Position'])
        tree.links.new(sub_math.inputs[1], att_stat.outputs['Min'])

        div_math = nodes.new('ShaderNodeVectorMath')
        div_math.operation = 'DIVIDE'
        tree.links.new(div_math.inputs[0], sub_math.outputs['Vector'])
        tree.links.new(div_math.inputs[1], att_stat.outputs['Range'])

        # Vector math node: scale (Texture coordinate scaling)
        scale_math = nodes.new('ShaderNodeVectorMath')
        scale_math.operation = 'SCALE'
        scale_math.inputs['Scale'].default_value = tex_coord_scale
        tree.links.new(scale_math.inputs[0], div_math.outputs['Vector'])

        # Img texture node
        img_tex_node = nodes.new('GeometryNodeImageTexture')
        img_tex_node.inputs['Image'].default_value = bpy.data.images.load(disp_map_path)
        tree.links.new(img_tex_node.inputs['Vector'], scale_math.outputs['Vector'])
        
        # Math node: multiply for height of map
        mul_math = nodes.new('ShaderNodeMath')
        mul_math.operation = 'MULTIPLY'
        mul_math.inputs[1].default_value = height_scale
        tree.links.new(mul_math.inputs[0], img_tex_node.outputs['Color'])
        
        # Combine XYZ:
        combine_xyz_node = nodes.new('ShaderNodeCombineXYZ')
        tree.links.new(combine_xyz_node.inputs['Z'], mul_math.outputs['Value'])
        
        # Set position
        set_pos_node = nodes.new('GeometryNodeSetPosition')
        tree.links.new(set_pos_node.inputs['Offset'], combine_xyz_node.outputs['Vector'])
        tree.links.new(set_pos_node.inputs['Geometry'], nodes['Group Input'].outputs['Geometry'])

        # Out
        tree.links.new(nodes['Group Output'].inputs['Geometry'], set_pos_node.outputs['Geometry'])
        
        


    def deactivate_material(self):
        assert self.node_background != None
        self.node_background.inputs[1].default_value = 0.0

    
    def reactivate_material(self):
        assert self.node_background != None
        self.node_background.inputs[1].default_value = 1.0


    def delete_material(self, obj):
        for material_slot in obj.material_slots:
            bpy.data.materials.remove(material_slot.material)
        self.delete_geo_node(obj.name + self.obj_name_ext)


    def delete_geo_node(self, geo_node):
        node_groups = bpy.data.node_groups
        if geo_node in node_groups:
            node_groups.remove(node_groups[geo_node])


    def set_random_material(self, obj):
        dirlist = os.listdir(self.path)
        texture_file = random.choice(dirlist)
        while not os.path.isdir(os.path.join(self.path,texture_file)):
            dirlist.remove(texture_file)
            texture_file = random.choice(dirlist)
        self.delete_material(obj)
        self.set_material(obj, os.path.join(self.path, texture_file))