import bpy
import time

from random import Random, seed

from .transform import transform


class scene():
    def __init__(self, engine='BLENDER_EEVEE', device=None) -> None:
        # bpy.context.scene.render.engine = 'CYCLES'
        # bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        # bpy.context.scene.cycles.device = 'GPU'
        seed(time.time())
        self.rand_gen = Random()
        self.engine = engine
        self.__device = device
        bpy.context.scene.render.engine = engine
        if self.engine == 'CYCLES' and self.__device is not None:
            bpy.context.scene.cycles.device = self.__device


    def randomize(self, objs, randomizations:list[transform]):
        for o in objs:
            for rnd in randomizations:
                rnd(o)


    def clean_up(self):
        # Delete all textures, materials and meshes
        for img in bpy.data.images:
            bpy.data.images.remove(img)
        for mesh in bpy.data.meshes:
            bpy.data.meshes.remove(mesh)
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)