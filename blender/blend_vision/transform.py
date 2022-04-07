from time import time
from random import Random, seed


class transform():
    def __init__(self, rnd_seed=None) -> None:
        if rnd_seed is None:
            seed(time())
        self.rand_gen = Random()
        self.transforms = []


    def __update_attr__(self, obj, attribute) -> None:
        obj_attr = getattr(obj, attribute)
        obj_attr_vals = []
        for _ in range(len(obj_attr)):
            obj_attr_vals.append(self.rand_gen.uniform(-2, 2))
        obj_attr = tuple(obj_attr_vals)
    
    
    def position(self, obj) -> None:
        self.__update_attr__(obj, 'location')


    def rotation(self, obj) -> None:
        self.__update_attr__(obj, 'rotation_quaternion')

    def set_transforms(self, transforms:list) -> None:
        self.transforms.extend(transforms)

    def get_transforms(self) -> list:
        return self.transforms


    