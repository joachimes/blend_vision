import bpy
import os
from time import time
from random import Random, seed

from .scene import scene


class render():
    def __init__(self, rnd_seed=None) -> None:
        if rnd_seed is None:
            seed(time())
        self.rand_gen = Random()

    
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


    def instance_label_objs(self, objs, label_colors:list[dict]=[]) -> None:
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        if len(objs) - len(label_colors) > 0:
            for i in range(len(objs) - len(label_colors)):
                label_colors.append({ 'R':self.rand_gen.uniform(0,1)
                                    , 'G':self.rand_gen.uniform(0,1)
                                    , 'B':self.rand_gen.uniform(0,1) })

        for o, label_color in zip(objs, label_colors[:len(objs)]):
            self.label_shader_setup(o, label_color)

    def semantic_label_setup(self, obj_collection, label_color:dict=None, sample_color:bool=False) -> dict:
        if label_color is None:
            label_color = {'R':0,'B':0,'G':0}
            if sample_color:
                label_color = { 'R':self.rand_gen.uniform(0,1)
                                , 'G':self.rand_gen.uniform(0,1)
                                , 'B':self.rand_gen.uniform(0,1) }
        for o in obj_collection:
            self.label_shader_setup(o, label_color)
        return label_color

    def semantic_label_reset(self, obj_collection):
        self.semantic_label_setup(obj_collection)

    # obj_dict = {'object':obj, 'label_color':dict}
    # label_color = {'R':float, 'B':float, 'G':float}
    def instance_segmentation_setup(self, scene_objs:list[dict]):
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        for obj_dict in scene_objs:
            self.label_shader_setup(obj_dict['object'], obj_dict['label_color'])

        

    def segmentation_reset(self, objs:list, scene:scene):
        bpy.context.scene.render.engine = scene.engine
        for o in objs:
            self.label_shader_reset(o)
