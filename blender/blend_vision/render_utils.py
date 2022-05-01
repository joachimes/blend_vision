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
        self.render_samples = bpy.context.scene.cycles.samples
        self.label_samples = 1

    
    def link_nodes(self, o_node_tree, input_node, output_node, input_node_target:str, output_node_target:str='Surface') -> None:
        o_node_tree.links.new(output_node.inputs[output_node_target]
                            , input_node.outputs[input_node_target])


    def label_shader_setup(self, o, color:dict) -> None:
        for material_slot in o.material_slots:
            node_tree = material_slot.material.node_tree
            combine_rgb_node = node_tree.nodes.new('ShaderNodeCombineRGB')
            diffuse_bsdf_node = node_tree.nodes.new('ShaderNodeBsdfDiffuse')

            node_tree.links.new(diffuse_bsdf_node.inputs['Color'], combine_rgb_node.outputs["Image"])
            node_tree.links.new(node_tree.nodes['Material Output'].inputs['Surface'], diffuse_bsdf_node.outputs['BSDF'])

            for val in combine_rgb_node.inputs:
                val.default_value = color[val.name]


    def label_shader_reset(self, o) -> None:
        for material_slot in o.material_slots:
            node_tree = material_slot.material.node_tree
            principled_bsdf_node = node_tree.nodes['Principled BSDF']
            material_output_node = node_tree.nodes['Material Output']
            node_tree.links.new(material_output_node.inputs['Surface'], principled_bsdf_node.outputs['BSDF'])
            

    def instance_label_objs(self, objs, label_colors:list[dict]=[]) -> None:
        bpy.context.scene.cycles.samples = self.label_samples

        if len(objs) - len(label_colors) > 0:
            for i in range(len(objs) - len(label_colors)):
                label_colors.append({ 'R':self.rand_gen.uniform(0,1)
                                    , 'G':self.rand_gen.uniform(0,1)
                                    , 'B':self.rand_gen.uniform(0,1) })

        for o, label_color in zip(objs, label_colors[:len(objs)]):
            self.label_shader_setup(o, label_color)


    def semantic_label_setup(self, obj_collection, label_color:dict=None, sample_color:bool=False) -> dict:
        bpy.context.scene.cycles.samples = self.label_samples
        if label_color is None:
            label_color = {'R':0,'B':0,'G':0}
            if sample_color:
                label_color = { 'R':self.rand_gen.uniform(0,1)
                                , 'G':self.rand_gen.uniform(0,1)
                                , 'B':self.rand_gen.uniform(0,1) }
        for o in obj_collection:
            self.label_shader_setup(o, label_color)
        return label_color


    def black_semantic_label(self, obj_collection):
        self.semantic_label_setup(obj_collection)


    def segmentation_reset(self, objs:list, scene:scene):
        bpy.context.scene.cycles.samples = self.render_samples
        for o in objs:
            self.label_shader_reset(o)
