import bpy
import os

class composition():
    def __init__(self) -> None:
        self.desired_nodes = ['CompositorNodeRLayers'
                        , 'CompositorNodeMath'
                        , 'CompositorNodeMapRange'
                        , 'CompositorNodeComposite']
        scene_context = bpy.context.scene
        scene_context.view_layers["ViewLayer"].use_pass_z = True
        scene_context.view_layers["ViewLayer"].use_pass_normal = True
        scene_context.view_layers["ViewLayer"].use_pass_diffuse_color = True
        scene_context.use_nodes = True
        self.tree = scene_context.node_tree


    def normal_depth_render(self):
        bpy.context.scene.use_nodes = True
        # clear default nodes
        for node in self.tree.nodes:
            self.tree.nodes.remove(node)

        scene_nodes = {}

        for node in self.desired_nodes:
            scene_nodes[node] = self.tree.nodes.new(type=node)

        # create input image node
        maps = ['Normal', 'Depth']
        ['Image', 'Depth', 'Normal']

        file_outputs = {}
        path_list = os.path.normpath(bpy.context.scene.render.filepath).split(os.path.sep)
        for map in maps:
            path_list[-2] = map
            file_outputs[map] = self.tree.nodes.new('CompositorNodeOutputFile')
            file_outputs[map].base_path = os.path.join(*path_list)

        # link nodes
        # Base image
        self.tree.links.new(scene_nodes['CompositorNodeComposite'].inputs['Image'], scene_nodes['CompositorNodeRLayers'].outputs['Image'])

        # Depth image
        scene_nodes['CompositorNodeMath'].operation = 'DIVIDE' 
        scene_nodes['CompositorNodeMath'].inputs[1].default_value = 100.0 # 
        self.tree.links.new(scene_nodes['CompositorNodeMath'].inputs[0], scene_nodes['CompositorNodeRLayers'].outputs['Depth'])
        self.tree.links.new(file_outputs['Depth'].inputs['Image'], scene_nodes['CompositorNodeMath'].outputs['Value'])

        # Normal image
        self.tree.links.new(file_outputs['Normal'].inputs['Image'], scene_nodes['CompositorNodeRLayers'].outputs['Normal'])


    def label_shading_render(self):
        bpy.context.scene.use_nodes = True
        # clear default nodes
        for node in self.tree.nodes:
            self.tree.nodes.remove(node)

        r_layer = self.tree.nodes.new(type='CompositorNodeRLayers')
        comp_layer = self.tree.nodes.new(type='CompositorNodeComposite')

        # link nodes
        self.tree.links.new(comp_layer.inputs['Image'], r_layer.outputs['DiffCol'])


    def composition_reset(self):
        scene_context = bpy.context.scene
        scene_context.use_nodes = False