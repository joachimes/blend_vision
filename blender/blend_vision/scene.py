import bpy
import time

from random import Random, seed

from .transform import transform


class scene():
    def __init__(self, engine='BLENDER_EEVEE', device=None) -> None:
        seed(time.time())
        self.rand_gen = Random()
        self.engine = engine
        self.__device = device
        bpy.context.scene.render.engine = engine
        bpy.context.scene.render.resolution_x = 256*4
        bpy.context.scene.render.resolution_y = 256*4
        if self.engine == 'CYCLES':
            bpy.context.scene.cycles.samples = 128
            bpy.context.scene.render.use_persistent_data = True
            if self.__device is not None:
                prefs = bpy.context.preferences.addons["cycles"].preferences
                prefs.get_devices()
                prefs.compute_device_type = 'CUDA'
                print(bpy.context.preferences.addons["cycles"].preferences.compute_device_type)
                prefs.compute_device = 'CUDA_0'
                # i = 0
                # for d in bpy.context.preferences.addons["cycles"].preferences.devices:
                    # d["use"] = 0
                    # if d["name"][:6] == 'NVIDIA' and i == 1:
                    # if d["name"][:6] == 'NVIDIA' and i == 0:
                        # d["use"] = 1
                        # i += 1
                    # print(d["name"], d["use"])
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