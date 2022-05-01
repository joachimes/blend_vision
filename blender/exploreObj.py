import bpy
import mathutils
import os
import glob
import json
import sys
import random
import time

dir = os.path.dirname(__file__)
if not dir in sys.path:
    sys.path.append(dir)
from blend_vision import scene, data, render, composition, hdri, texture, placement, camera

def main():
    # Rendering n_scenes * n_img
    data_dict = {"data_dir": os.path.join(os.path.dirname(__file__), '..', 'data'),
                "dataset_name": 'ShapeNetCore.v2',
                "json_name": 'shapenetcore.taxonomy.json',
                "model_name": 'model_normalized.obj',
                "hdri_folder_path": 'hdri',
                "render_folder": 'Generated',
                "target_classes": ['camera', 'table', 'lamp', 'couch', 'car'],
                "hierarchy": {'table':['camera', 'lamp'], 'Background':['table', 'couch', 'car']},
                "class_paths": {},
                "num_obj_min": 1,
                "num_obj_max": 2,
                "engine": 'CYCLES',
                "device": 'GPU',
                "camera_target": {'x':0,'y':0,'z':0},
                "cam_radius": list(range(1,5)),
                "n_scenes": 50,
                "n_img": 10
                }
    
    scene_param_dict = {}
    
    scene_data = data(data_dict)
    scene_obj = scene(engine=scene_data.engine, device=scene_data.device)
    scene_hdri = hdri(os.path.join(scene_data.data_dir, scene_data.hdri_folder_path))
    scene_render = render()
    scene_comp = composition()
    scene_camera = camera()
    obj_texture = texture(os.path.join(scene_data.data_dir, 'textures'))

    scene_data.load_obj_paths()

    target_folder = scene_data.render_folder

    scene_obj.clean_up()
    scene_placement = placement()
    semantic_labels = {}
    for scene_id in range(scene_data.n_scenes):
        class_collection = bpy.data.collections.new('Background')
        bpy.ops.mesh.primitive_plane_add(size=50, location=(0,0,0))
        check_collection = [o for o in bpy.context.scene.collection.objects]
        for o in bpy.context.selected_objects:
            class_collection.objects.link(o)
            obj_texture.set_random_material(o)
            if check_collection:
                bpy.context.scene.collection.objects.unlink(o)

        scene_hdri.set_random_hdri()
        scene_data.load_data()
        img_id = str(time.time())
        for img_num in range(scene_data.n_img):
            scene_hdri.deactivate_hdri()

            # Set transforms and prepare for label pass
            for item in scene_data.hierarchy:
                if item in bpy.data.collections:
                    target_collection = bpy.data.collections[item]
                    obj_collections = [bpy.data.collections[obj_col] for obj_col in scene_data.hierarchy[item] if obj_col in bpy.data.collections]
                    scene_placement.scatter_objs_on_target_collection(target_collection, obj_collections)
            
            for collection in bpy.data.collections:
                if collection.name in ['Collection', 'Background']:
                    continue
                scene_render.semantic_label_reset(collection.objects) #
                    

            scene_camera.update_camera_pos(scene_data.camera_target, random.choice(scene_data.cam_radius))
            # Set no material for label image
            scene_render.semantic_label_reset(bpy.data.collections['Background'].objects) #
            # Render Semantic label pass
            bpy.context.scene.render.image_settings.color_mode = 'BW'
            for collection in bpy.data.collections:
                if collection.name in ['Collection', 'Background']:
                    continue
                scene_render.semantic_label_setup(obj_collection=collection.objects, label_color={'R':1.0,'G':1.0, 'B':1.0})
                bpy.context.scene.render.filepath = os.path.join(scene_data.data_dir, target_folder, 'Semantic_labels', collection.name, img_id + '_' + str(scene_id) + '_' + str(img_num))
                bpy.ops.render.render(write_still = True)
                scene_render.semantic_label_reset(obj_collection=collection.objects)
            bpy.context.scene.render.image_settings.color_mode = 'RGB'


            # Render single semantic label pass
            for collection in bpy.data.collections:
                if collection.name in ['Collection']:
                    continue
                if collection.name in semantic_labels.keys():
                    semantic_color = scene_render.semantic_label_setup(obj_collection=collection.objects, label_color=semantic_labels[collection.name])
                else:
                    semantic_color = scene_render.semantic_label_setup(obj_collection=collection.objects, sample_color=True)
                    semantic_labels[collection.name] = semantic_color
            bpy.context.scene.render.filepath = os.path.join(scene_data.data_dir, target_folder, 'Semantic_labels', img_id + '_' + str(scene_id) + '_' + str(img_num))
            bpy.ops.render.render(write_still = True)
            scene_render.semantic_label_reset(obj_collection=collection.objects)

            # Render instance label pass
            scene_render.instance_label_objs(bpy.data.objects)
            bpy.context.scene.render.filepath = os.path.join(scene_data.data_dir, target_folder, 'Instance_labels', img_id + '_' + str(scene_id) + '_' + str(img_num))
            bpy.ops.render.render(write_still = True)

            # Reset shading before final render
            scene_hdri.reactivate_hdri()
            scene_render.segmentation_reset(objs=bpy.data.objects, scene=scene_obj)


            # Render final pass
            scene_comp.composition_setup()
            bpy.context.scene.render.filepath = os.path.join(scene_data.data_dir, target_folder, 'Renders', img_id + '_' + str(scene_id) + '_' + str(img_num))
            bpy.ops.render.render(write_still = True)
            scene_comp.composition_reset()

        # Remove Collection
        for collection in bpy.data.collections:
            if collection.name == "Collection":
                continue
            bpy.data.collections.remove(collection)

        scene_obj.clean_up()



if __name__ == '__main__':
    main()