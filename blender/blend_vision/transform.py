from time import time
from random import Random, seed


class transform():
    def __init__(self, rnd_seed=None) -> None:
        if rnd_seed is None:
            seed(time())
        self.rand_gen = Random()
        self.transforms = []


    def __update_attr__(self, obj, attribute, rng=2) -> None:
        obj_attr = getattr(obj, attribute)
        obj_attr_vals = []
        for _ in range(len(obj_attr)):
            obj_attr_vals.append(self.rand_gen.uniform(-rng, rng))
        obj_attr = type(obj_attr)(obj_attr_vals)
        return obj_attr
    
    
    def position(self, obj) -> None:
        obj.location = self.__update_attr__(obj, 'location')


    def rotation(self, obj) -> None:
        obj.rotation_euler = self.__update_attr__(obj, 'rotation_euler', rng=6)


    def scale(self, obj) -> None:
        rnd_val = self.rand_gen.uniform(-5, 5)
        obj.scale = type(getattr(obj, 'scale'))([rnd_val, rnd_val, rnd_val])


    def set_transforms(self, transforms:list) -> None:
        self.transforms.extend(transforms)


    def get_transforms(self) -> list:
        return self.transforms


    