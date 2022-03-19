#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import sys
import fbx


def initializeScene():
    """
    Initializes the sdk manager and the scene

    Returns:
        (list): SDK Manager as first index, scene as second index.
    """
    # the first thing to do is to create the FBX SDK manager which is the
    # object allocator for almost all the classes in the SDK.
    manager = fbx.FbxManager.Create()
    if not manager:
        sys.exit(0)

    # Create an IOSettings object
    ios = fbx.FbxIOSettings.Create(manager, fbx.IOSROOT)
    manager.SetIOSettings(ios)

    # Create the entity that will hold the scene.
    scene = fbx.FbxScene.Create(manager, "")

    return manager, scene


def configureIO(manager, embed_media=True):
    """
    Configures the input/output settings for the given FBX SDK manager.

    Args:
        manager (fbx.FbxManager): Manager that handles all FBX SDK calls.

        embed_media (boolean): Value for the embedded media property.
    """
    manager.GetIOSettings().SetBoolProp(fbx.EXP_FBX_MATERIAL, True)
    manager.GetIOSettings().SetBoolProp(fbx.EXP_FBX_TEXTURE, True)
    manager.GetIOSettings().SetBoolProp(fbx.EXP_FBX_EMBEDDED, embed_media)
    manager.GetIOSettings().SetBoolProp(fbx.EXP_FBX_SHAPE, True)
    manager.GetIOSettings().SetBoolProp(fbx.EXP_FBX_GOBO, True)
    manager.GetIOSettings().SetBoolProp(fbx.EXP_FBX_ANIMATION, True)
    manager.GetIOSettings().SetBoolProp(fbx.EXP_FBX_GLOBAL_SETTINGS, True)


def saveScene(manager, scene, file_path, file_format=-1, embed_media=False):
    """
    Saves the FBX scene to the given file path.

    Args:
        manager (fbx.FbxManager): Manager object that handles all SDK calls.

        scene (fbx.FbxScene): Scene object that will be saved onto given file_path.

        file_path (string): Path to save FBX to.

        file_format (int): File format to save this as. Ascii or Binary.

        embed_media (boolean): If True, will include embed media.

    Returns:
        (boolean): Result of export.
    """
    exporter = fbx.FbxExporter.Create(manager, "")
    if file_format < 0 or file_format >= manager.GetIOPluginRegistry().GetWriterFormatCount():
        file_format = manager.GetIOPluginRegistry().GetNativeWriterFormat()
        if not embed_media:
            format_count = manager.GetIOPluginRegistry().GetWriterFormatCount()
            for format_index in range(format_count):
                if manager.GetIOPluginRegistry().WriterIsFBX(format_index):
                    description = manager.GetIOPluginRegistry().GetWriterFormatDescription(format_index)
                    if "ascii" in description:
                        file_format = format_index
                        break

    if not manager.GetIOSettings():
        ios = fbx.FbxIOSettings.Create(manager, fbx.IOSROOT)
        manager.SetIOSettings(ios)

    configureIO(manager, embed_media)

    result = exporter.Initialize(file_path, file_format, manager.GetIOSettings())
    if result is True:
        result = exporter.Export(scene)

    exporter.Destroy()
    return result


def loadScene(manager, scene, file_path):
    """
    Loads the given file_path fbx onto memory to edit.

    Args:
        manager (fbx.FbxManager): Manager object that handles all SDK calls.

        scene (fbx.FbxScene): Scene object that file path will be loaded onto.

        file_path (string): FBX path to load.

    Returns:
        (boolean): Result of import.
    """
    importer = fbx.FbxImporter.Create(manager, "")
    result = importer.Initialize(file_path, -1, manager.GetIOSettings())

    if not result:
        return False

    if importer.IsFBX():
        configureIO(manager)

    result = importer.Import(scene)
    importer.Destroy()
    return result


class PiperFBX(object):
    """
    This is a helper FBX class useful in accessing and modifying the FBX Scene Documentation for the FBX SDK
    https://help.autodesk.com/view/FBX/2015/ENU/?guid=__cpp_ref_index_html

    Thanks to Randall for writing most of this class.
    https://gist.github.com/Meatplowz/8f408912cf554f2d11085fb68b62d3a3

    Example:
        fbx_file = PiperFBX(r'c:/my_path/character.fbx')
        fbx_file.removeMaterialsAndTextures()
        fbx_file.save()  # ALWAYS SAVE OR CLOSE! Save closes the sdk_manager.
    """
    def __init__(self, filename):
        """
        FBX Scene Object
        """
        self.filename = filename
        self.scene = None
        self.sdk_manager = None
        self.sdk_manager, self.scene = initializeScene()
        loadScene(self.sdk_manager, self.scene, filename)

        self.root_node = self.scene.GetRootNode()
        self.scene_nodes = self.getSceneNodes()

    def close(self):
        """
        You need to run this to close the FBX scene safely
        """
        # destroy objects created by the sdk
        self.sdk_manager.Destroy()

    def __getSceneNodesRecursive(self, node):
        """
        Recursive method to get all scene nodes
        this should be private, called by getSceneNodes()
        """
        self.scene_nodes.append(node)
        for i in range(node.GetChildCount()):
            self.__getSceneNodesRecursive(node.GetChild(i))

    @staticmethod
    def __castPropertyType(fbx_property):
        """
        Cast a property to type to properly get the value
        """
        unsupported_types = [fbx.eFbxUndefined, fbx.eFbxChar, fbx.eFbxUChar, fbx.eFbxShort, fbx.eFbxUShort,
                             fbx.eFbxUInt, fbx.eFbxLongLong, fbx.eFbxHalfFloat, fbx.eFbxDouble4x4, fbx.eFbxEnum,
                             fbx.eFbxTime, fbx.eFbxReference, fbx.eFbxBlob, fbx.eFbxDistance, fbx.eFbxDateTime,
                             fbx.eFbxTypeCount]

        # property is not supported or mapped yet
        property_type = fbx_property.GetPropertyDataType().GetType()
        if property_type in unsupported_types:
            return None

        if property_type == fbx.eFbxBool:
            casted_property = fbx.FbxPropertyBool1(fbx_property)
        elif property_type == fbx.eFbxDouble:
            casted_property = fbx.FbxPropertyDouble1(fbx_property)
        elif property_type == fbx.eFbxDouble2:
            casted_property = fbx.FbxPropertyDouble2(fbx_property)
        elif property_type == fbx.eFbxDouble3:
            casted_property = fbx.FbxPropertyDouble3(fbx_property)
        elif property_type == fbx.eFbxDouble4:
            casted_property = fbx.FbxPropertyDouble4(fbx_property)
        elif property_type == fbx.eFbxInt:
            casted_property = fbx.FbxPropertyInteger1(fbx_property)
        elif property_type == fbx.eFbxFloat:
            casted_property = fbx.FbxPropertyFloat1(fbx_property)
        elif property_type == fbx.eFbxString:
            casted_property = fbx.FbxPropertyString(fbx_property)
        else:
            raise ValueError(
                'Unknown property type: {0} {1}'.format(fbx_property.GetPropertyDataType().GetName(), property_type))

        return casted_property

    def getSceneNodes(self):
        """
        Get all nodes in the fbx scene
        """
        self.scene_nodes = []
        for i in range(self.root_node.GetChildCount()):
            self.__getSceneNodesRecursive(self.root_node.GetChild(i))
        return self.scene_nodes

    def getTypeNodes(self, type_node):
        """
        Get nodes from the scene with the given type

        display_layer_nodes = fbx_file.getTypeNodes( u'DisplayLayer' )
        """
        nodes = []
        num_objects = self.scene.RootProperty.GetSrcObjectCount()
        for i in range(0, num_objects):
            node = self.scene.RootProperty.GetSrcObject(i)
            if node:
                if node.GetTypeName() == type_node:
                    nodes.append(node)
        return nodes

    def getClassNodes(self, class_id):
        """
        Get nodes in the scene with the given class id

        geometry_nodes = fbx_file.getClassNodes( fbx.FbxGeometry.ClassId )
        """
        nodes = []
        num_nodes = self.scene.RootProperty.GetSrcObjectCount(fbx.FbxCriteria.ObjectType(class_id))
        for index in range(0, num_nodes):
            node = self.scene.RootProperty.GetSrcObject(fbx.FbxCriteria.ObjectType(class_id), index)
            if node:
                nodes.append(node)
        return nodes

    @staticmethod
    def getProperty(node, property_string):
        """
        Gets a property from an Fbx node

        export_property = fbx_file.getProperty(node, 'no_export')
        """
        fbx_property = node.FindProperty(property_string)
        return fbx_property

    def getPropertyValue(self, node, property_string):
        """
        Gets the property value from an Fbx node

        property_value = fbx_file.getPropertyValue(node, 'no_export')
        """
        fbx_property = node.FindProperty(property_string)
        if fbx_property.IsValid():
            # cast to correct property type so you can get
            casted_property = self.__castPropertyType(fbx_property)
            if casted_property:
                return casted_property.Get()
        return None

    def deleteNodesWithPropertyValue(self, property_string, match_value):
        """
        Deletes nodes with the given property string set to the given match value

        Args:
            property_string (string): Name of property to try and find.

            match_value (any): Value to to match to delete node.

        Returns:
            (list): Nodes deleted.
        """
        deleted = []
        self.getSceneNodes()

        for node in self.scene_nodes:
            value = self.getPropertyValue(node, property_string)

            if value is None or value != match_value:
                continue

            node_name = node.GetName()
            self.scene.DisconnectSrcObject(node)
            self.scene.RemoveNode(node)
            deleted.append(node_name)

        return deleted

    def getNodeByName(self, name):
        """
        Get the fbx node by name
        """
        self.getSceneNodes()
        # right now this is only getting the first one found
        node = [node for node in self.scene_nodes if node.GetName() == name]
        if node:
            return node[0]
        return None

    def removeNamespace(self):
        """
        Remove all namespaces from all nodes

        This is not an ideal method but
        """
        self.getSceneNodes()
        for node in self.scene_nodes:
            orig_name = node.GetName()
            split_by_colon = orig_name.split(':')
            if len(split_by_colon) > 1:
                new_name = split_by_colon[-1:][0]
                node.SetName(new_name)
        return True

    def removeNodeProperty(self, node, property_string):
        """
        Remove a property from an Fbx node

        remove_property = fbx_file.remove_property(node, 'PropertyNameHere')
        """
        node_property = self.getProperty(node, property_string)
        if node_property.IsValid():
            node_property.DestroyRecursively()
            return True
        return False

    def removeNodesByNames(self, names):
        """
        Remove nodes from the fbx file from a list of names

        names = ['object1','shape2','joint3']
        remove_nodes = fbx_file.remove_nodes_by_names(names)
        """
        if names is None or len(names) == 0:
            return True

        self.getSceneNodes()
        remove_nodes = [node for node in self.scene_nodes if node.GetName() in names]
        for node in remove_nodes:
            self.scene.DisconnectSrcObject(node)
            self.scene.RemoveNode(node)
        self.getSceneNodes()
        return True

    def removeTextures(self):
        """
        Removes all textures from the scene.
        """
        for i in range(self.scene.GetTextureCount()):
            texture = self.scene.GetTexture(i)
            self.scene.RemoveTexture(texture)

    def removeMaterials(self):
        """
        Removes all materials from the scene.
        """
        for i in range(self.scene.GetMaterialCount()):
            material = self.scene.GetMaterial(i)
            self.scene.RemoveMaterial(material)

    def removeMaterialsAndTextures(self):
        """
        Removes all textures and materials from the scene.
        """
        self.removeTextures()
        self.removeMaterials()

    def save(self, filename=None):
        """
        Save the current fbx scene as the incoming filename .fbx
        """
        # save as a different filename
        filename = filename if filename else self.filename
        saveScene(self.sdk_manager, self.scene, filename)
        self.close()
