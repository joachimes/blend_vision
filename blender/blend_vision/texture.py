import bpy
import os
import random

class texture():
    def __init__(self, path:str) -> None:
        self.path = path


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
            path_type = path[len(base_name):len(base_name)+3]
            new_img_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
            new_img_node.image = bpy.data.images.load(os.path.join(texPath, path))
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
            
            elif path_type == 'dis': # Displacement map
                disp_node = mat.node_tree.nodes.new('ShaderNodeDisplacement')
                disp_node.inputs['Scale'].default_value = 0.02
                mat.node_tree.links.new(disp_node.inputs['Height'], node_output)
                mat.node_tree.links.new(mat_output.inputs['Displacement'], disp_node.outputs['Displacement'])
                
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


    def deactivate_material(self):
        assert self.node_background != None
        self.node_background.inputs[1].default_value = 0.0

    
    def reactivate_material(self):
        assert self.node_background != None
        self.node_background.inputs[1].default_value = 1.0

    def delete_material(self, obj):
        for material_slot in obj.material_slots:
            bpy.data.materials.remove(material_slot.material)

    def set_random_material(self, obj):
        texture_file = random.choice(os.listdir(self.path))
        self.delete_material(obj)
        self.set_material(obj, os.path.join(self.path, texture_file))