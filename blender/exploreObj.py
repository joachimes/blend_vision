import bpy
import mathutils
import os
import glob
import json
import sys
import random

dir = os.path.dirname(__file__)
if not dir in sys.path:
    sys.path.append(dir)
from blend_vision import scene, data, render, transform, composition, hdri, texture


def main():

    data_dir = './data'
    dataset_name = 'ShapeNetCore.v2'
    json_name = 'shapenetcore.taxonomy.json'
    model_name = 'model_normalized.obj'
    target_classes = ['camera']
    hdri_folder_path = 'hdri'

    scene_obj = scene(engine='CYCLES', device='GPU')
    scene_obj.clean_up()
    scene_data = data()
    scene_hdri = hdri(os.path.join(scene_data.data_dir, scene_data.hdri_folder_path))
    scene_render = render()
    scene_transform = transform()
    scene_transform.set_transforms([scene_transform.position, scene_transform.rotation])
    scene_comp = composition()
    obj_texture = texture(os.path.join(scene_data.data_dir, 'textures'))

    scene_data.load_obj_paths()
    # scene_data.render_path()

    scene_hdri.set_random_hdri()


    
    bpy.ops.mesh.primitive_plane_add(size=50, location=(0,0,-2))
    for obj in bpy.data.collections['Collection'].objects:
        if 'Camera' not in obj.name and 'Light' not in obj.name:
            obj_texture.set_random_material(obj)

    for class_path in scene_data.class_paths:
        class_collection = bpy.data.collections.new(class_path)
        bpy.context.scene.collection.children.link(class_collection)
        
        model_files = glob.glob(os.path.join(scene_data.data_dir, scene_data.dataset_name, class_path, '**', '*.obj'), recursive=True)
        sample_amount = random.randint(1,5)#(5, 20)
        model_files_sample = random.sample(model_files, sample_amount)
 
        for i, model_file in enumerate(model_files_sample):

            # Parse path
            model_file_split = model_file.split('/')
            model_hash_index = -2
            if model_file_split[-2] == 'models':
                model_hash_index = -3

            # Import
            bpy.ops.import_scene.obj(filepath=model_file)
            
            obj_name = model_file_split[-1].replace('.obj', '')
            
            # Init collection
            # Check if mesh is in collection
            check_collection = [i for i in bpy.context.scene.collection.objects]
            # add mesh to correct collection
            for o in bpy.context.selected_objects:
                class_collection.objects.link(o)
                
                if check_collection:
                    bpy.context.scene.collection.objects.unlink(o)
            
            if i > 10:
                break

        scene_render.semantic_label_reset(class_collection.objects) #
        scene_obj.randomize(class_collection.objects, scene_transform.get_transforms())
    scene_hdri.deactivate_hdri()
    for collection in bpy.data.collections:
        if collection.name in ['Collection']:
            continue
        scene_render.semantic_label_setup(obj_collection=collection.objects, sample_color=True)
        bpy.context.scene.render.filepath = os.path.join(scene_data.data_dir, 'Labels', collection.name, model_file_split[model_hash_index])
        bpy.ops.render.render(write_still = True)
        scene_render.semantic_label_reset(obj_collection=collection.objects)

    # Render instance label pass
    bpy.context.scene.render.filepath = os.path.join(scene_data.data_dir, 'Labels', model_file_split[model_hash_index])
    scene_render.instance_label_objs(bpy.data.objects)
    bpy.ops.render.render(write_still = True)

    # Reset shading before final render
    scene_hdri.reactivate_hdri()
    scene_render.segmentation_reset(objs=bpy.data.objects, scene=scene_obj)


    # Render final pass
    scene_comp.composition_setup()
    bpy.context.scene.render.filepath = os.path.join(scene_data.data_dir, 'Renders', model_file_split[model_hash_index])
    bpy.ops.render.render(write_still = True)
    scene_comp.composition_reset()

    # Remove Collection
    # bpy.data.collections.remove(myCol)

    scene_obj.clean_up()



if __name__ == '__main__':
    main()