import bpy
from .scene import scene

class render():
    def __init__(self) -> None:
        pass

    def check_color():
        pass

    def label_shader_setup(o, color:dict):
        new_node = 'ShaderNodeCombineRGB' #'ShaderNodeRGB', 
        for material_slot in o.material_slots:
            o_node_tree = material_slot.material.node_tree
            new_node_obj = o_node_tree.nodes.new(new_node)
            mat_out_node = o_node_tree.nodes['Material Output']

            o_node_tree.nodes.links.new(mat_out_node.inputs['Surface'], new_node_obj.outputs['Image'])
            for val in new_node_obj.inputs:
                val = color[val.name]

    def label_shader_reset(o):
        for material_slot in o.material_slots:
            o_node_tree = material_slot.material.node_tree
            new_node_obj = o_node_tree.nodes['Principled BSDF']
            mat_out_node = o_node_tree.nodes['Material Output']

            o_node_tree.nodes.links.new(mat_out_node.inputs['Surface'], new_node_obj.outputs['BSDF'])


    # obj_dict = {'object':obj, 'label_color':dict}
    # label_color = {'R':float, 'B':float, 'G':float}
    def segmentation_setup(self, scene_objs:list):
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        for obj_dict in scene_objs:
            self.label_shader_setup(obj_dict['object'], obj_dict['label_color'])

    def segmentation_reset(self, scene_objs:list, scene:scene):
        bpy.context.scene.render.engine = scene._engine
        for obj in scene_objs:
            self.label_shader_reset(obj)

    def composition_setup():
        # switch on nodes and get reference
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree

        # clear default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        scene_nodes = []
        desired_nodes = ['CompositorNodeRLayers', 'CompositorNodeMath', 'CompositorNodeInvert', 'CompositorNodeMath', 'CompositorNodeOutputFile']
        for node in desired_nodes:
            if node == 'CompositorNodeRLayers':
                compositor_node = tree.nodes.new(type=node)
            else:
                scene_nodes.append(tree.nodes.new(type=node))

        # create input image node
        ['normal', 'class_segmentation', 'object_segmentation', 'depth']

        ['Image', 'Mist', 'Normal', 'IndexOB']

        # link nodes
        links = tree.links
        link = links.new(compositor_node.outputs[0], scene_nodes[0].inputs[0])
