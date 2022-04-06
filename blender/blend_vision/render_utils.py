import bpy
from .scene import scene
from random import Random
class render():
    def __init__(self) -> None:
        pass


    def check_color(self):
        pass

    
    def link_nodes(self, o_node_tree, input_node, output_node, input_node_target:str, output_node_target:str='Surface') -> None:
        o_node_tree.links.new(output_node.inputs[output_node_target]
                            , input_node.outputs[input_node_target])


    def label_shader_setup(self, o, color:dict) -> None:
        new_node = 'ShaderNodeCombineRGB' #'ShaderNodeRGB', 
        for material_slot in o.material_slots:
            o_node_tree = material_slot.material.node_tree
            new_node_obj = o_node_tree.nodes.new(new_node)
            self.link_nodes(o_node_tree, new_node_obj
                            , o_node_tree.nodes['Material Output']
                            , input_node_target='Image')

            for val in new_node_obj.inputs:
                val.default_value = color[val.name]


    def label_shader_reset(self, o) -> None:
        for material_slot in o.material_slots:
            o_node_tree = material_slot.material.node_tree
            new_node_obj = o_node_tree.nodes['Principled BSDF']
            self.link_nodes(o_node_tree, new_node_obj
                            , o_node_tree.nodes['Material Output']
                            , input_node_target='BSDF')


    def label_objs(self, objs, label_colors:list[dict]=[]) -> None:
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        if len(objs) - len(label_colors) > 0:
            rand_gen = Random()
            for i in range(len(objs) - len(label_colors)):
                label_colors.append({ 'R':rand_gen.uniform(0,1)
                                    , 'G':rand_gen.uniform(0,1)
                                    , 'B':rand_gen.uniform(0,1) })

        print(label_colors)
        for o, color in zip(objs, label_colors[:len(objs)]):
            self.label_shader_setup(o, color)


    # obj_dict = {'object':obj, 'label_color':dict}
    # label_color = {'R':float, 'B':float, 'G':float}
    def segmentation_setup(self, scene_objs:list[dict]):
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        for obj_dict in scene_objs:
            self.label_shader_setup(obj_dict['object'], obj_dict['label_color'])


    def segmentation_reset(self, objs:list, scene:scene):
        bpy.context.scene.render.engine = scene.engine
        for o in objs:
            self.label_shader_reset(o)


    def composition_setup(self):
        scene_context = bpy.context.scene
        scene_context.view_layers["ViewLayer"].use_pass_z = True
        scene_context.view_layers["ViewLayer"].use_pass_normal = True

        # switch on nodes and get reference
        scene_context.use_nodes = True
        tree = scene_context.node_tree

        # clear default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        scene_nodes = {}
        desired_nodes = ['CompositorNodeRLayers'
                        , 'CompositorNodeMath'
                        , 'CompositorNodeMapRange'
                        , 'CompositorNodeOutputFile']
        for node in desired_nodes:
            scene_nodes[node] = tree.nodes.new(type=node)

        # create input image node
        ['normal', 'depth']
        ['Image', 'Depth', 'Normal']


        # link nodes
        output_node = scene_nodes['CompositorNodeOutputFile']
        output_node.base_path = bpy.context.scene.render.filepath

        # Base image
        tree.links.new(output_node.inputs['Image'], scene_nodes['CompositorNodeRLayers'].outputs['Image'])

        # Depth image
        scene_nodes['CompositorNodeMath'].opertation = 'DIVIDE' 
        scene_nodes['CompositorNodeMath'].inputs[1].default_value = 100 # 
        tree.links.new(scene_nodes['CompositorNodeMath'].inputs[0], scene_nodes['CompositorNodeRLayers'].outputs['Depth'])
        tree.links.new(output_node.inputs['Depth'], scene_nodes['CompositorNodeMath'].outputs['Value'])

        # Normal image
        tree.links.new(output_node.inputs['Normal'], scene_nodes['CompositorNodeRLayers'].outputs['Normal'])


    def composition_reset(self):
        scene_context = bpy.context.scene
        scene_context.use_nodes = False