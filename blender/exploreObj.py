import bpy
import os
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
    data_dict = {'data_dir': os.path.join(os.path.dirname(__file__), '..', 'data'),
                'dataset_name': 'ShapeNetCore.v2',
                'json_name': 'shapenetcore.taxonomy.json',
                'model_extension': 'obj',
                'hdri_folder_path': 'hdri',
                'texture_folder_path': 'textures',
                'render_folder': os.path.join(os.path.dirname(__file__), '..', 'data', 'Generated'),
                'target_classes': ['airplane', 'wastebin', 'suitcase', 'handbasket', 'bench', 'bottle', 'autobus', 'tin can', 'automobile', 'spigot', 'lamp', 'mailbox', 'motorcycle', 'flowerpot', 'tower', 'train'],
                'class_paths': {},
                'engine': 'CYCLES',
                'device': 'GPU',
                'num_obj_min': 5,
                'num_obj_max': 30,
                'n_scenes': 500,
                'n_img': 100
                }
    render_param_dict = {'render_folder':'Generated','labels':['instance', 'semantic', 'normal', 'depth'], 'semantic':['automobile'], 'semantic_label_colors':{}}
    # render_param_dict = {'render_folder':'Generated','labels':['semantic', 'normal', 'depth'], 'semantic':['automobile'], 'semantic_label_colors':{}}

    scene_param_dict = {'hierarchy': {'Background':['airplane', 'wastebin', 'suitcase', 'handbasket', 'bench', 'bottle', 'autobus'
                                                    , 'tin can', 'automobile', 'spigot', 'lamp', 'mailbox', 'motorcycle', 'flowerpot', 'tower', 'train'],
                                        'wastebin':['tin can', 'bottle'],
                                        'bench':['tin can', 'suitcase', 'bottle']
                                    },
                        'big':['airplane', 'lamp', 'flowerpot', 'tower', 'train'],
                        'medium':['autobus', 'automobile', 'motorcycle', 'flowerpot'],
                        'small':['airplane', 'wastebin', 'suitcase', 'handbasket', 'bench', 'bottle', 'tin can', 'automobile', 'spigot', 'lamp', 'mailbox', 'flowerpot' ],
                        'camera_target': {'x':0,'y':0,'z':0},
                        'cam_radius': list(range(1,5)),
                        }
    
    scene_data = data(data_dict)
    scene_obj = scene(engine=scene_data.engine, device=scene_data.device)
    scene_render = render(scene_data.render_folder)
    scene_comp = composition()
    scene_camera = camera()
    scene_hdri = hdri(os.path.join(scene_data.data_dir, scene_data.hdri_folder_path))
    obj_texture = texture(os.path.join(scene_data.data_dir, scene_data.texture_folder_path))

    scene_data.load_obj_paths()

    semantic_renders = scene_data.target_classes
    if render_param_dict['semantic'] != None:
        semantic_renders = render_param_dict['semantic']
    target_folder = scene_data.render_folder

    scene_obj.clean_up()
    scene_placement = placement()
    semantic_labels = render_param_dict['semantic_label_colors']
    for scene_id in range(scene_data.n_scenes):
        scene_data.load_base_scene()
        scene_data.load_data()
        img_id = str(time.time())
        for img_num in range(scene_data.n_img):
            img_name = img_id + '_' + str(scene_id) + '_' + str(img_num)
            
            for o in bpy.data.collections['Background'].objects:
                obj_texture.set_random_material(o)
            # Set transforms
            for item in scene_param_dict['hierarchy']:
                if item in bpy.data.collections:
                    target_collection = bpy.data.collections[item]
                    obj_collections = [bpy.data.collections[obj_col] for obj_col in scene_param_dict['hierarchy'][item] if obj_col in bpy.data.collections]
                    scene_placement.scatter_objs_on_target_collection(target_collection, obj_collections)
            
            scene_hdri.set_random_hdri()
            scene_hdri.deactivate_hdri() 
            scene_camera.update_camera_pos(scene_param_dict['camera_target'], random.choice(scene_param_dict['cam_radius']))
                    

            if 'semantic' in render_param_dict['labels']:
                # Set material to black for label images
                for collection in bpy.data.collections:
                    if collection.name in ['Collection']:
                        continue
                    scene_render.black_semantic_label(collection.objects)
                scene_comp.label_shading_render()
                # Render separate semantic label pass
                print(semantic_renders)
                scene_render.render_separate_semantic_labels(semantic_renders, img_name)
                # Render single semantic label pass
                scene_render.render_full_semantic_label(semantic_labels, img_name)


            if 'instance' in render_param_dict['labels']:
                # Render instance label pass
                scene_render.render_instance_label(img_name)


            # Reset shading before final render
            scene_render.segmentation_reset(objs=bpy.data.objects)
            scene_hdri.reactivate_hdri()

            # Render final pass
            scene_comp.normal_depth_render()
            bpy.context.scene.render.filepath = os.path.join(target_folder, 'Renders', img_name)
            bpy.ops.render.render(write_still = True)
            scene_comp.composition_reset()

        # Remove Collection
        for collection in bpy.data.collections:
            if collection.name == 'Collection':
                continue
            bpy.data.collections.remove(collection)

        scene_obj.clean_up()



if __name__ == '__main__':
    main()