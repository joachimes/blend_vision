from json import load
from glob import glob
from os import mkdir, remove
from os.path import join, exists


class data():
    def __init__(self,paths='./data') -> None:
        # Read yaml file and extract data
        self.data_dir = paths
        self.dataset_name = 'ShapeNetCore.v2'
        self.json_name = 'shapenetcore.taxonomy.json'
        self.model_name = 'model_normalized.obj'
        self.target_classes = ['camera']
        self.class_paths = []

    def load_obj_paths(self) -> None:
        with open(join(self.data_dir, self.json_name)) as f:
            dataset_json = load(f)
        
        for class_obj in dataset_json:
            for target_class in self.target_classes:
                if target_class in class_obj['metadata']['label'] and exists(join(self.data_dir, self.dataset_name, class_obj['metadata']['name'])):
                    print(class_obj['metadata']['label'], class_obj['metadata']['numInstances'])
                    self.class_paths += [class_obj['metadata']['name']]
                if not exists(join(self.data_dir, self.dataset_name, class_obj['metadata']['name'])):
                    pass
                    # print(f"Data for class {class_obj['metadata']['label']} does not exist")
        


    def render_path(self) -> None:
        # setup correct folder path
        if not exists(join(self.data_dir, 'renders')):
            mkdir(join(self.data_dir, 'renders'))
        else:
            # Cleaning old renders
            for img in glob(join(self.data_dir, 'renders', '*.png')):
                remove(img)
