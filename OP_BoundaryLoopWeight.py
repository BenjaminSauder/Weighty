import bpy
import bmesh

from . import OP_Base


class OP_BoundaryLoopWeight(bpy.types.Operator, OP_Base.OP_MeshBase):
    """Sets the bevel weight or crease values from a face selection to the corresponding boundary loop edges"""
    bl_idname = "mesh.boundary_loop_weight"
    bl_label = "Boundary Loop Weight"
    bl_options = {'REGISTER', 'UNDO'}

    weight: bpy.props.FloatProperty(
        name="Weight", default=1.0, min=0.0, max=1.0)
    clear_inner_weights: bpy.props.BoolProperty(
        name="Clear Inner Weights", default=True)
    weight_type: bpy.props.EnumProperty(
        name="Type",
        description="Select the weight type",
        items=[("Bevel", "Bevel", ""),
               ("Crease", "Crease", ""),
               ],
      )

    @classmethod
    def poll(cls, context):
        result = OP_Base.OP_MeshBase.active_object_is_mesh(context)
        return result and OP_Base.OP_MeshBase.is_select_mode('FACE')

    def execute(self, context):
     
        use_bevel_weight = "Bevel" == self.weight_type
        use_crease_weight = "Crease" == self.weight_type

        for obj in context.selected_objects:
            if not self.is_mesh_in_editmode(obj):
                continue

            bm = bmesh.from_edit_mesh(obj.data)

            if use_bevel_weight:
                bevel_layer = bm.edges.layers.bevel_weight.verify()

            if use_crease_weight:
                crease_layer = bm.edges.layers.crease.verify()

            selected_faces = [face for face in bm.faces if face.select]
            if len(selected_faces) == 0:
                continue

            boundary_edges = set()
            inner_edges = set()

            for face in selected_faces:
                for loop in face.loops:
                    if not loop.link_loop_radial_next.face.select:
                        boundary_edges.add(loop.edge)
                    elif self.clear_inner_weights:
                        inner_edges.add(loop.edge)

            for edge in boundary_edges:
                if use_bevel_weight:
                    edge[bevel_layer] = self.weight
                if use_crease_weight:
                    edge[crease_layer] = self.weight

            if self.clear_inner_weights:
                for edge in inner_edges:
                    if use_bevel_weight:
                        edge[bevel_layer] = 0
                    if use_crease_weight:
                        edge[crease_layer] = 0

            bmesh.update_edit_mesh(
                obj.data, loop_triangles=False, destructive=False)

        return {'FINISHED'}

    def invoke(self, context, event):       
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, "weight")
        col.prop(self, "clear_inner_weights")

        layout.use_property_split = True
        col.prop(self, "weight_type", expand=True)
