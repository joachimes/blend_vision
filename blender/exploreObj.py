import bpy
import os
import glob
import json



data_dir = '/home/joachimes/dtu/graphicslab/data'
dataset_name = 'ShapeNetCore.v2'
json_name = 'shapenetcore.taxonomy.json'
model_name = 'model_normalized.obj'
target_classes = ['camera']

bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'



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


# setup correct folder path
if not os.path.exists(os.path.join(data_dir, 'renders')):
    os.mkdir(os.path.join(data_dir, 'renders'))
else:
    # Cleaning old renders
    for img in glob.glob(os.path.join(data_dir, 'renders', '*.png')):
        os.remove(img)

for class_path in class_paths:
    
    model_files = glob.glob(os.path.join(data_dir, dataset_name, class_path, '**', '*.obj'), recursive=True)
    i = 0
    for model_file in model_files:
        
        # Parse path
        model_file_split = model_file.split('/')
        model_hash_index = -2
        if model_file_split[-2] == 'models':
            model_hash_index = -3

        # Import
        bpy.ops.import_scene.obj(filepath=model_file)
        
        
        collection_name = model_file_split[model_hash_index]
        obj_name = model_file_split[-1].replace('.obj', '')
        
        
        # Init collection
        myCol = bpy.data.collections.new(collection_name)
        # Are these lines needed?
        obj_object = bpy.context.selected_objects[0]
        bpy.context.scene.collection.children.link(myCol)
        # add mesh to correct collection
        for ob in bpy.context.selected_objects:
            myCol.objects.link(ob)
            bpy.context.scene.collection.objects.unlink(ob)
        
        # Render pass
        bpy.context.scene.render.filepath = os.path.join(data_dir, 'renders', model_file_split[model_hash_index])
        bpy.ops.render.render(write_still = True)


        # Remove Collection
        bpy.data.collections.remove(myCol)

        # Delete all textures, materials and meshes
        for img in bpy.data.images:
            bpy.data.images.remove(img)
        for mesh in bpy.data.meshes:
            bpy.data.meshes.remove(mesh)
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)

