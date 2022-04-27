import bpy
from mathutils import Matrix, Vector

import random
from json import load
from glob import glob
from os import mkdir, remove
from os.path import join, exists


class data():
    def __init__(self, paths='./data') -> None:
        # Read yaml file and extract data
        self.data_dir = paths
        self.dataset_name = 'ShapeNetCore.v2'
        self.json_name = 'shapenetcore.taxonomy.json'
        self.model_name = 'model_normalized.obj'
        self.hdri_folder_path = 'hdri'
        self.target_classes = ['camera', 'table', 'lamp', 'car', 'couch']
        self.hierarchy = {'table':['camera', 'lamp'], 'Background':self.target_classes}
        self.class_paths = {}
        self.num_obj_min = 1
        self.num_obj_max = 2


    def load_obj_paths(self) -> None:
        with open(join(self.data_dir, self.json_name)) as f:
            dataset_json = load(f)
        
        for class_obj in dataset_json:
            for target_class in self.target_classes:
                if target_class in class_obj['metadata']['label'] and exists(join(self.data_dir, self.dataset_name, class_obj['metadata']['name'])):
                    print(class_obj['metadata']['label'], class_obj['metadata']['numInstances'])
                    self.class_paths[target_class] = class_obj['metadata']['name']
                if not exists(join(self.data_dir, self.dataset_name, class_obj['metadata']['name'])):
                    pass
                    # print(f"Data for class {class_obj['metadata']['label']} does not exist")
        
    

    def load_data(self):
        for class_path in self.class_paths:
            class_collection = bpy.data.collections.new(class_path)
            bpy.context.scene.collection.children.link(class_collection)

            model_files = glob(join(self.data_dir, self.dataset_name, self.class_paths[class_path], '**', '*.obj'), recursive=True)
            sample_amount = random.randint(self.num_obj_min,self.num_obj_max)
            model_files_sample = random.sample(model_files, sample_amount)
    
            for i, model_file in enumerate(model_files_sample):

                # Parse path
                model_file_split = model_file.split('/')
                model_hash_index = -2
                if model_file_split[-2] == 'models':
                    model_hash_index= -3

                # Import
                bpy.ops.import_scene.obj(filepath=model_file)
                
                obj_name = model_file_split[-1].replace('.obj', '')
                
                # Init collection
                # Check if mesh is in collection
                check_collection = [i for i in bpy.context.scene.collection.objects]
                # add mesh to correct collection
                for o in bpy.context.selected_objects:
                    # Should this be called somewhere else?
                    self.move_pivot_to_bottom(o)
                    self.apply_transfrom(o, use_rotation=True, use_location=True)

                    o.hide_render = True
                    class_collection.objects.link(o)

                    if check_collection:
                        bpy.context.scene.collection.objects.unlink(o)


    #https://blender.stackexchange.com/questions/159538/how-to-apply-all-transformations-to-an-object-at-low-level
    def apply_transfrom(self, obj, use_location=False, use_rotation=False, use_scale=False):
        mb = obj.matrix_basis
        I = Matrix()
        loc, _, scale = mb.decompose()

        # rotation
        T = Matrix.Translation(loc)
        R = mb.to_3x3().normalized().to_4x4()
        S = Matrix.Diagonal(scale).to_4x4()

        transform = [I, I, I]
        basis = [T, R, S]
        
        if use_location:
            transform[0], basis[0] = basis[0], transform[0]
        if use_rotation:
            transform[1], basis[1] = basis[1], transform[1]
        if use_scale:
            transform[2], basis[2] = basis[2], transform[2]
            
        M = transform[0] @ transform[1] @ transform[2]
        if hasattr(obj.data, "transform"):
            obj.data.transform(M)
        for c in obj.children:
            c.matrix_local = M @ c.matrix_local
            
        obj.matrix_basis = basis[0] @ basis[1] @ basis[2]


    def move_pivot_to_bottom(self, obj):
        m = obj.matrix_world

        lowest = min((m @ v.co)[2] for v in obj.data.vertices)
        difference = Vector((0,0,obj.location.z - lowest))
        local_difference = difference @ m
        for v in obj.data.vertices:
            v.co += local_difference
        m.translation -= difference


    def render_path(self) -> None:
        # setup correct folder path
        if not exists(join(self.data_dir, 'renders')):
            mkdir(join(self.data_dir, 'renders'))
        else:
            # Cleaning old renders
            for img in glob(join(self.data_dir, 'renders', '*.png')):
                remove(img)
