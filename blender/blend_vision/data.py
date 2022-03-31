class data():
    def __init__(self,paths) -> None:
        # Read yaml file and extract data
        self.data_dir = './data'
        self.dataset_name = 'ShapeNetCore.v2'
        self.json_name = 'shapenetcore.taxonomy.json'
        self.model_name = 'model_normalized.obj'
        self.target_classes = ['camera']