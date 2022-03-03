import bpy
import os
import glob
import json


data_dir = '/home/joachimes/dtu/graphicslab/data'

dataset_name = 'ShapeNetCore.v2'
json_name = 'shapenetcore.taxonomy.json'

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.render.engine = 'BLENDER_EEVEE'


target_classes = ['camera']

with open(os.path.join(data_dir, json_name)) as f:
    dataset_json = json.load(f)

class_paths = []
for class_obj in dataset_json:
    for target_class in target_classes:
        if target_class in class_obj['metadata']['label'] and os.path.exists(os.path.join(data_dir, dataset_name, class_obj['metadata']['name'])):
            print(class_obj['metadata']['label'], class_obj['metadata']['numInstances'])
            class_paths += [class_obj['metadata']['name']]
        if not os.path.exists(os.path.join(data_dir, dataset_name, class_obj['metadata']['name'])):
            print(f'Data for class {class_obj["metadata"]["label"]} does not exist')
print(class_paths)
model_name = 'model_normalized.obj'

if not os.path.exists(os.path.join(data_dir, 'renders')):
    os.mkdir(os.path.join(data_dir, 'renders'))
else:
    for img in glob.glob(os.path.join(data_dir, 'renders', '*.png')):
        os.remove(img)

for class_path in class_paths:
    print(os.path.join(data_dir, dataset_name, class_path, '**', '*.obj'))
    
    model_files = glob.glob(os.path.join(data_dir, dataset_name, class_path, '**', '*.obj'), recursive=True)
    print(model_files)

    for model_file in model_files:
        model_file_split = model_file.split('/')
        model_hash_index = -2
        if model_file_split[-2] == 'models':
            model_hash_index = -3
        collection_name = model_file_split[model_hash_index]
        obj_name = model_file_split[-1].replace('.obj', '')
        bpy.ops.import_scene.obj(filepath=model_file)
        obj_object = bpy.context.selected_objects[0]
        myCol = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(myCol)
        for ob in bpy.context.selected_objects:
            myCol.objects.link(ob)
            bpy.context.scene.collection.objects.unlink(ob)
        bpy.context.scene.render.filepath = os.path.join(data_dir, 'renders', model_file_split[model_hash_index])
        bpy.ops.render.render(write_still = True)
        # if bpy.context.object.mode == 'EDIT':
        #     bpy.ops.object.mode_set(mode='OBJECT')
        # deselect all objects
        # bpy.ops.object.select_all(action='DESELECT')
        # select the object
        # bpy.data.objects[].select_set(True)
        # delete all selected objects
        # bpy.ops.object.delete()
        bpy.data.collections.remove(myCol)

        for collec in bpy.data.collections:
            if not collec.users:
                print("no users")
        for img in bpy.data.images:
            if not img.users:
                print("no users")
        for mesh in bpy.data.meshes:
            if not mesh.users:
                print("No users for mesh")

        break

