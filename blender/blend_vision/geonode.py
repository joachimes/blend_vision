from ctypes.wintypes import tagRECT
import bpy


class placement():
    def __init__(self) -> None:
        self.node_types = ['GeometryNodeDistributePointsOnFaces',
                    'FunctionNodeRandomValue',
                    'GeometryNodeInstanceOnPoints',
                    'GeometryNodeJoinGeometry',
                    'GeometryNodeInputNormal',
                    'GeometryNodeAttributeTransfer',
                    'FunctionNodeCompare',
                    'ShaderNodeSeparateXYZ',
                    'GeometryNodeRealizeInstances']

    def setup(self, obj, collections:list, pick_instance:bool=False):
        modifier = None
        if 'GeometryNodes' in obj.modifiers:
            modifier = obj.modifiers['GeometryNodes']
            self.shuffle_modifier(modifier)
            return
        else:
            modifier = obj.modifiers.new(obj.name, type='NODES')
        tree = modifier.node_group
        nodes = tree.nodes

        node_dict = {'NodeGroupInput': nodes['Group Input'],
            'NodeGroupOutput': nodes['Group Output']}
        for node in self.node_types:
            node_dict[node] = nodes.new(node)

        
        # FunctionNodeCompare
        node_dict['FunctionNodeCompare'].operation = 'GREATER_EQUAL'
        node_dict['FunctionNodeCompare'].data_type = 'FLOAT'
        node_dict['FunctionNodeCompare'].inputs['B'].default_value = 0.05

        node_dict['GeometryNodeAttributeTransfer'].data_type = 'FLOAT_VECTOR'
        tree.links.new(node_dict['GeometryNodeAttributeTransfer'].inputs['Source'], node_dict['NodeGroupInput'].outputs['Geometry'])
        tree.links.new(node_dict['GeometryNodeAttributeTransfer'].inputs['Attribute'], node_dict['GeometryNodeInputNormal'].outputs['Normal'])
        tree.links.new(node_dict['ShaderNodeSeparateXYZ'].inputs['Vector'],node_dict['GeometryNodeAttributeTransfer'].outputs['Attribute'])
        tree.links.new(node_dict['FunctionNodeCompare'].inputs['A'], node_dict['ShaderNodeSeparateXYZ'].outputs['Z'])
        

        node_dict['GeometryNodeDistributePointsOnFaces'].inputs['Distance Min'].default_value = 0.6
        node_dict['GeometryNodeDistributePointsOnFaces'].inputs['Density Max'].default_value = 900.
        tree.links.new(node_dict['GeometryNodeDistributePointsOnFaces'].inputs['Mesh'], node_dict['NodeGroupInput'].outputs['Geometry'])
        tree.links.new(node_dict['GeometryNodeDistributePointsOnFaces'].inputs['Selection'], node_dict['FunctionNodeCompare'].outputs['Result'])


        # Add collection and join
        collection_join = nodes.new('GeometryNodeJoinGeometry')
        for collection in collections:
            new_collection = nodes.new('GeometryNodeCollectionInfo')
            new_collection.inputs['Collection'].default_value = collection
            new_collection.inputs['Separate Children'].default_value = True
            new_collection.inputs['Reset Children'].default_value = True
            tree.links.new(collection_join.inputs['Geometry'], new_collection.outputs['Geometry'])


        # Everything going into InstanceOnPoints node
        if pick_instance:
            node_dict['GeometryNodeInstanceOnPoints'].inputs['Pick Instance'].default_value = True
        tree.links.new(node_dict['GeometryNodeInstanceOnPoints'].inputs['Instance'], collection_join.outputs['Geometry'])
        tree.links.new(node_dict['GeometryNodeInstanceOnPoints'].inputs['Points'], node_dict['GeometryNodeDistributePointsOnFaces'].outputs['Points'])
        tree.links.new(node_dict['GeometryNodeInstanceOnPoints'].inputs['Rotation'], node_dict['GeometryNodeDistributePointsOnFaces'].outputs['Rotation'])
        tree.links.new(node_dict['GeometryNodeInstanceOnPoints'].inputs['Scale'], node_dict['FunctionNodeRandomValue'].outputs['Value'])
        
        node_dict['FunctionNodeRandomValue'].inputs['Min'].default_value[0] = 0.1
        node_dict['FunctionNodeRandomValue'].inputs['Max'].default_value[0] = 0.4
        
        # Join InstanceOnPoint geometry with original geometry
        tree.links.new(node_dict['GeometryNodeRealizeInstances'].inputs['Geometry'], node_dict['GeometryNodeInstanceOnPoints'].outputs['Instances'])
        tree.links.new(node_dict['GeometryNodeJoinGeometry'].inputs['Geometry'], node_dict['GeometryNodeRealizeInstances'].outputs['Geometry'])
        tree.links.new(node_dict['GeometryNodeJoinGeometry'].inputs['Geometry'], node_dict['NodeGroupInput'].outputs['Geometry'])

    def scatter_objs_on_target_collection(self, target_collection, objs_collections, pick_instance):
        for target in target_collection.objects:
            self.setup(target, objs_collections, pick_instance)
    
    def shuffle_modifier(self, modifier):
        pass


