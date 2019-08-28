import bpy
import bmesh
import mathutils

from . import OP_Base

class Macro_TweakLinkedByWeight(bpy.types.Macro):
    bl_idname = "mesh.tweak_linked_by_weight"
    bl_label = "Tweak Linked By Weight Boundary"
    bl_options = {'REGISTER', 'UNDO'}

class OP_SelectLinkedByWeightBoundary(bpy.types.Operator, OP_Base.OP_MeshBase):
    bl_idname = "mesh.select_linked_by_weight_boundary"
    bl_label = "Select Linked By Weight Boundary"
    bl_options = {'REGISTER', 'UNDO'}

    threshold_face: bpy.props.FloatProperty(
        name="Threshold", default=1.0, min=0.0, max=1.0)

    weight: bpy.props.FloatProperty(
        name="Weight", default=1.0, min=0.0, max=1.0)

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
  
    def invoke(self, context, event):

        self.initial_pos = mathutils.Vector((event.mouse_x, event.mouse_y))
        self.centers = {}
        self.edges = {}

        use_bevel_weight = "Bevel" == self.weight_type
        use_crease_weight = "Crease" == self.weight_type

        #TODO set active obj?
        bpy.ops.mesh.select_linked_by_weight('INVOKE_DEFAULT', weight_type=self.weight_type, threshold_face=self.threshold_face)

        for obj in context.selected_objects:
            if not self.is_mesh_in_editmode(obj):
                continue

            bm = bmesh.from_edit_mesh(obj.data)    
        
            selected_faces = [face for face in bm.faces if face.select]
            if len(selected_faces) == 0 or len(selected_faces) == len(bm.faces):
                continue

            boundary_edges = set()
            for face in selected_faces:
                for loop in face.loops:
                    if not loop.link_loop_radial_next.face.select:
                        boundary_edges.add(loop.edge)

            for face in bm.faces:
                face.select = False

            for edge in bm.edges:
                edge.select = edge in boundary_edges                    
                
        bpy.context.tool_settings.mesh_select_mode = False, True, False
    
        return {'FINISHED'}


    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "threshold_face")
        col.prop(self, "weight")
        layout.use_property_split = True
        col.prop(self, "weight_type", expand=True)
