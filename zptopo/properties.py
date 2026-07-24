import bpy

from bpy.props import (
    IntProperty,
    PointerProperty,
    StringProperty,
)


class ZPTOPO_PG_state(bpy.types.PropertyGroup):
    object_name: StringProperty(
        name="Object Name",
        default="",
    )

    vertex_count: IntProperty(
        name="Vertices",
        default=0,
        min=0,
    )

    edge_count: IntProperty(
        name="Edges",
        default=0,
        min=0,
    )

    face_count: IntProperty(
        name="Faces",
        default=0,
        min=0,
    )

    uv_layer_name: StringProperty(
        name="UV Layer",
        default="",
    )

    uv_loop_count: IntProperty(
        name="UV Loops",
        default=0,
        min=0,
    )

    uv_island_count: IntProperty(
        name="UV Islands",
        default=0,
        min=0,
    )

    uv_boundary_edge_count: IntProperty(
        name="UV Boundary Edges",
        default=0,
        min=0,
    )

    uv_closed_loop_count: IntProperty(
        name="Closed Boundary Loops",
        default=0,
        min=0,
    )

    uv_open_chain_count: IntProperty(
        name="Open Boundary Chains",
        default=0,
        min=0,
    )
    uv_ordered_loop_count: IntProperty(
        name="Ordered Boundary Loops",
        default=0,
        min=0,
    )

    uv_failed_loop_order_count: IntProperty(
        name="Failed Loop Orders",
        default=0,
        min=0,
    )
    uv_detected_corner_count: IntProperty(
        name="Detected Corners",
        default=0,
        min=0,
    )

    uv_loops_with_corners: IntProperty(
        name="Loops With Corners",
        default=0,
        min=0,
    )

    uv_loops_without_corners: IntProperty(
        name="Loops Without Corners",
        default=0,
        min=0,
    )

    uv_maximum_corner_count: IntProperty(
        name="Most Corners In Loop",
        default=0,
        min=0,
    )

    uv_minimum_corner_count: IntProperty(
        name="Fewest Corners In Loop",
        default=0,
        min=0,
    )

    largest_loop_edge_count: IntProperty(
        name="Largest Loop",
        default=0,
        min=0,
    )

    smallest_loop_edge_count: IntProperty(
        name="Smallest Loop",
        default=0,
        min=0,
    )


classes = (
    ZPTOPO_PG_state,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.zptopo_state = PointerProperty(
        type=ZPTOPO_PG_state
    )


def unregister():
    if hasattr(bpy.types.Scene, "zptopo_state"):
        del bpy.types.Scene.zptopo_state

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)