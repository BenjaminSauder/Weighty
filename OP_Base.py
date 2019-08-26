import bpy


class OP_MeshBase():

    @classmethod
    def active_object_is_mesh(cls, context):
        return context.active_object is not None and OP_MeshBase.is_mesh_in_editmode(context.active_object)

    @classmethod
    def is_mesh_in_editmode(cls, obj):
        return obj.type == "MESH" and obj.mode == 'EDIT'

    @classmethod
    def is_select_mode(cls, mode):
        vert, edge, face = bpy.context.tool_settings.mesh_select_mode

        if mode == 'VERT':
            return vert and not edge and not face
        if mode == 'EDGE':
            return edge and not vert and not face
        if mode == 'FACE':
            return face and not vert and not edge
