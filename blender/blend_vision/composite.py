import bpy
import os

class composition():
    def __init__(self) -> None:
        self.desired_nodes = ['CompositorNodeRLayers'
                        , 'CompositorNodeMath'
                        , 'CompositorNodeMapRange'
                        , 'CompositorNodeComposite']


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

        for node in self.desired_nodes:
            scene_nodes[node] = tree.nodes.new(type=node)

        # create input image node
        maps = ['Normal', 'Depth']
        ['Image', 'Depth', 'Normal']

        file_outputs = {}
        path_list = os.path.normpath(bpy.context.scene.render.filepath).split(os.path.sep)
        for map in maps:
            path_list[-2] = map
            file_outputs[map] = tree.nodes.new('CompositorNodeOutputFile')
            file_outputs[map].base_path = os.path.join(*path_list)

        # link nodes
        # Base image
        tree.links.new(scene_nodes['CompositorNodeComposite'].inputs['Image'], scene_nodes['CompositorNodeRLayers'].outputs['Image'])

        # Depth image
        scene_nodes['CompositorNodeMath'].operation = 'DIVIDE' 
        scene_nodes['CompositorNodeMath'].inputs[1].default_value = 100 # 
        tree.links.new(scene_nodes['CompositorNodeMath'].inputs[0], scene_nodes['CompositorNodeRLayers'].outputs['Depth'])
        tree.links.new(file_outputs['Depth'].inputs['Image'], scene_nodes['CompositorNodeMath'].outputs['Value'])

        # Normal image
        tree.links.new(file_outputs['Normal'].inputs['Image'], scene_nodes['CompositorNodeRLayers'].outputs['Normal'])


    def composition_reset(self):
        scene_context = bpy.context.scene
        scene_context.use_nodes = False