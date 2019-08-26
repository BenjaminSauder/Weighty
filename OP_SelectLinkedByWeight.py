import bpy
import bmesh

from . import OP_Base


class OP_SelectLinkedByWeight(bpy.types.Operator,  OP_Base.OP_MeshBase):
    """Sets the bevel weight or crease values from a face selection to the corresponding boundary loop edges"""
    bl_idname = "mesh.select_linked_by_weight"
    bl_label = "Select Linked By Weight"
    bl_options = {'REGISTER', 'UNDO'}

    threshold_edge: bpy.props.FloatProperty(
        name="Threshold", default=0.0, min=0.0, max=1.0)
    threshold_face: bpy.props.FloatProperty(
        name="Threshold", default=1.0, min=0.0, max=1.0)

    
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
        if result:
            edge_mode = OP_Base.OP_MeshBase.is_select_mode('EDGE')
            face_mode = OP_Base.OP_MeshBase.is_select_mode('FACE')
            return edge_mode or face_mode

        return False

    def execute(self, context):
        
        self.use_bevel_weight = "Bevel" == self.weight_type
        self.use_crease_weight = "Crease" == self.weight_type

        for obj in context.selected_objects:
            if not self.is_mesh_in_editmode(obj):
                continue

            self.bm = bmesh.from_edit_mesh(obj.data)
            if self.use_bevel_weight:
                self.bevel_layer = self.bm.edges.layers.bevel_weight.verify()

            if self.use_crease_weight:
                self.crease_layer = self.bm.edges.layers.crease.verify()

            if self.is_select_mode('FACE'):
               self.handle_face_mode()

            if self.is_select_mode('EDGE'):
                self.handle_edge_mode()

            bmesh.update_edit_mesh(
                obj.data, loop_triangles=False, destructive=False)

        return {'FINISHED'}

    def handle_edge_mode(self):
        selected_edges = set([edge for edge in self.bm.edges if edge.select])
        if len(selected_edges) == 0:
            return

        visited = set()
        while len(selected_edges) > 0:
            edge = selected_edges.pop()

            if edge not in visited:
                visited = self.search_linked_edges(edge, visited)

        for edge in visited:
            edge.select = True
            
    def search_linked_edges(self, edge, visited):
        candidates = {edge}
        current = edge
                
        if self.use_bevel_weight:
            layer = self.bevel_layer
        else:
            layer = self.crease_layer

        value = edge[layer]

        while current:
            for vert in current.verts:
                for loop in vert.link_loops:
                    edge_value = loop.edge[layer]

                    # just in case someone wants to select non weighted edges
                    abs_min = 0.01
                    if value == 0:
                        abs_min = 0 

                    if max(value - self.threshold_edge, abs_min) <= edge_value and edge_value <= (value + self.threshold_edge):
                        next_edge = loop.edge
                        if next_edge not in visited:
                            candidates.add(next_edge)

            visited.add(current)

            if len(candidates) > 0:
                current = candidates.pop()
            else:
                current = None

        return visited


    def handle_face_mode(self):
        selected_faces = set([face for face in self.bm.faces if face.select])
        if len(selected_faces) == 0:
            return

        visited = set()
        while len(selected_faces) > 0:
            face = selected_faces.pop()

            if face not in visited:
                visited = self.search_face_island(face, visited)

        for face in visited:
            face.select = True

    def search_face_island(self, face, visited):

        candidates = {face}
        current = face

        if self.use_bevel_weight:
            layer = self.bevel_layer
        else:
            layer = self.crease_layer

        while current:
            for loop in current.loops:
                if loop.edge[layer] < self.threshold_face:
                    next_face = loop.link_loop_radial_next.face
                    if next_face not in visited:
                        candidates.add(next_face)

            visited.add(current)

            if len(candidates) > 0:
                current = candidates.pop()
            else:
                current = None

        return visited

    def invoke(self, context, event):
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        if self.is_select_mode('EDGE'):
            col.prop(self, "threshold_edge")
        else:
            col.prop(self, "threshold_face")
        
        layout.use_property_split = True
        col.prop(self, "weight_type", expand=True)
