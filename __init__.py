# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy

bl_info = {
    "name": "Weighty",
    "author": "Benjamin Sauder",
    "description": "Small helper utilities for working with bevel weights and creases",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Mesh"
}

from . import (
    OP_BoundaryLoopWeight,
    OP_SelectLinkedByWeight,
    OP_TweakLinkedByWeight,
)

classes = [
    OP_BoundaryLoopWeight.OP_BoundaryLoopWeight,
    OP_SelectLinkedByWeight.OP_SelectLinkedByWeight,
    OP_TweakLinkedByWeight.OP_SelectLinkedByWeightBoundary,
    OP_TweakLinkedByWeight.Macro_TweakLinkedByWeight,
]


def select_linked_menu(self, context):
    layout = self.layout
    # layout.separator()
    # layout.operator_context = "INVOKE_DEFAULT"
    layout.operator(OP_SelectLinkedByWeight.OP_SelectLinkedByWeight.bl_idname)


def face_mesh_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator_context = "INVOKE_DEFAULT"
    layout.operator(OP_BoundaryLoopWeight.OP_BoundaryLoopWeight.bl_idname)
    layout.operator(OP_TweakLinkedByWeight.Macro_TweakLinkedByWeight.bl_idname)


def register():
    for c in classes:
        bpy.utils.register_class(c)
        
    op_macro = OP_TweakLinkedByWeight.Macro_TweakLinkedByWeight.define("MESH_OT_select_linked_by_weight_boundary")
    op_macro.properties.threshold_face = 0.1
    OP_TweakLinkedByWeight.Macro_TweakLinkedByWeight.define("TRANSFORM_OT_edge_bevelweight")

    bpy.types.VIEW3D_MT_edit_mesh_select_linked.append(select_linked_menu)
    bpy.types.VIEW3D_MT_edit_mesh_faces.append(face_mesh_menu)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.VIEW3D_MT_edit_mesh_select_linked.remove(select_linked_menu)
    bpy.types.VIEW3D_MT_edit_mesh_faces.remove(face_mesh_menu)
