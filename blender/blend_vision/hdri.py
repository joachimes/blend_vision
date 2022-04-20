import bpy
import os
import random

class hdri():
    def __init__(self, path:str) -> None:
        self.path = path
        self.node_background = None


    def set_hdri(self, path) -> None:
        node_tree = bpy.context.scene.world.node_tree
        tree_nodes = node_tree.nodes
        tree_nodes.clear()

        # Add Background node
        self.node_background = tree_nodes.new(type='ShaderNodeBackground')

        # Add Environment Texture node
        node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
        # Load and assign the image to the node property
        node_environment.image = bpy.data.images.load(path) # Relative path
        node_environment.location = -300,0

        # Add Output node
        node_output = tree_nodes.new(type='ShaderNodeOutputWorld')   
        node_output.location = 200,0

        # Link all nodes
        links = node_tree.links
        link = links.new(node_environment.outputs["Color"], self.node_background.inputs["Color"])
        link = links.new(self.node_background.outputs["Background"], node_output.inputs["Surface"])


    def deactivate_hdri(self):
        assert self.node_background != None
        self.node_background.inputs[1].default_value = 0.0

    def reactivate_hdri(self):
        assert self.node_background != None
        self.node_background.inputs[1].default_value = 1.0


    def set_random_hdri(self) -> None:
        hdri_file = random.choice(os.listdir(self.path))
        print(os.path.join(self.path, hdri_file))
        self.set_hdri(os.path.join(self.path, hdri_file))
