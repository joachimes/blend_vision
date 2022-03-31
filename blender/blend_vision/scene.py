from itertools import cycle
import bpy


class scene():
    def __init__(self, engine='BLENDER_EEVEE', device=None) -> None:
        self.__engine = engine
        self.__device = device
        bpy.context.scene.render.engine = self.__engine
        if self.__engine == 'CYCLES':
            bpy.context.scene.cycles.device = self.__device

    def __getattribute__(self, __name: str) -> any:
        return __name

    def clean_up():
        # Delete all textures, materials and meshes
        for img in bpy.data.images:
            bpy.data.images.remove(img)
        for mesh in bpy.data.meshes:
            bpy.data.meshes.remove(mesh)
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)