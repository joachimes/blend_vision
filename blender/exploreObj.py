import bpy
import mathutils
import os
import glob
import json
import sys
import random
import time
import math

dir = os.path.dirname(__file__)
if not dir in sys.path:
    sys.path.append(dir)
from blend_vision import scene, data, render, transform, composition, hdri, texture


def look_at(obj_camera, point):
    loc_camera = obj_camera.location#obj_camera.matrix_world.to_translation()

    direction = mathutils.Vector(point) - loc_camera
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')

    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()

def main():
    n_img = 10
    camera_target = {'x':0,'y':0,'z':1}
    cam_radius = 4
    scene_obj = scene(engine='CYCLES', device='GPU')
    scene_data = data()
    scene_hdri = hdri(os.path.join(scene_data.data_dir, scene_data.hdri_folder_path))
    scene_render = render()
    scene_transform = transform()
    scene_transform.set_transforms([scene_transform.position, scene_transform.rotation, scene_transform.scale])
    scene_comp = composition()
    obj_texture = texture(os.path.join(scene_data.data_dir, 'textures'))

    scene_data.load_obj_paths()
    # scene_data.render_path()

    scene_obj.clean_up()
    scene_hdri.set_random_hdri()


    bpy.ops.mesh.primitive_plane_add(size=50, location=(0,0,-2))
    for obj in bpy.data.collections['Collection'].objects:
        if 'Camera' not in obj.name and 'Light' not in obj.name:
            obj_texture.set_random_material(obj)


    scene_data.load_data()
    semantic_labels = {}
    img_id = str(time.time())

    for img_num in range(n_img):
        scene_hdri.deactivate_hdri()
        # Set transforms and prepare for label pass
        for collection in bpy.data.collections:
            if collection.name in ['Collection']:
                continue
            scene_obj.randomize(collection.objects, scene_transform.get_transforms())
            scene_render.semantic_label_reset(collection.objects) #
        

        #Update camera position
        cam = bpy.data.objects['Camera']
        t_loc_x = camera_target['x']
        t_loc_y = camera_target['y']

        alpha = random.random()*math.tau
        cam.location.x = t_loc_x+math.cos(alpha) * cam_radius# * math.sin(z)
        cam.location.y = t_loc_y+math.sin(alpha) * cam_radius# * math.sin(z)
        # cam.location.z = r*math.cos(z)

        look_at(cam, camera_target.values())
        
        # Render Semantic label pass
        bpy.context.scene.render.image_settings.color_mode = 'BW'
        for collection in bpy.data.collections:
            if collection.name in ['Collection']:
                continue
            scene_render.semantic_label_setup(obj_collection=collection.objects, label_color={'R':1.0,'G':1.0, 'B':1.0})
            bpy.context.scene.render.filepath = os.path.join(scene_data.data_dir, 'Generated', 'Semantic_labels', collection.name, img_id + '_' + str(img_num))
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
        bpy.context.scene.render.filepath = os.path.join(scene_data.data_dir, 'Generated', 'Semantic_labels', img_id + '_' + str(img_num))
        bpy.ops.render.render(write_still = True)
        scene_render.semantic_label_reset(obj_collection=collection.objects)

        # Render instance label pass
        bpy.context.scene.render.filepath = os.path.join(scene_data.data_dir,'Generated', 'Instance_labels', img_id + '_' + str(img_num))
        scene_render.instance_label_objs(bpy.data.objects)
        bpy.ops.render.render(write_still = True)

        # Reset shading before final render
        scene_hdri.reactivate_hdri()
        scene_render.segmentation_reset(objs=bpy.data.objects, scene=scene_obj)


        # Render final pass
        scene_comp.composition_setup()
        bpy.context.scene.render.filepath = os.path.join(scene_data.data_dir, 'Generated', 'Renders', img_id+ '_' + str(img_num))
        bpy.ops.render.render(write_still = True)
        scene_comp.composition_reset()

    # Remove Collection
    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection)

    scene_obj.clean_up()



if __name__ == '__main__':
    main()