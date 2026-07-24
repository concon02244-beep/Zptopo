import bpy


class ZPTOPO_PT_main_panel(bpy.types.Panel):
    bl_label = "Zptopo"
    bl_idname = "ZPTOPO_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Zptopo"

    def draw(self, context):
        layout = self.layout
        state = context.scene.zptopo_state

        layout.label(text="Garment Retopology")
        layout.separator()

        layout.operator(
            "zptopo.test",
            text="Test Addon",
            icon="CHECKMARK",
        )

        layout.operator(
            "zptopo.read_uv",
            text="Read UV",
            icon="GROUP_UVS",
        )

        layout.operator(
            "zptopo.select_uv_boundary_edges",
            text="Select UV Boundary Edges",
            icon="EDGESEL",
        )

        layout.separator()

        box = layout.box()

        box.label(
            text="UV Information",
            icon="GROUP_UVS",
        )

        if not state.object_name:
            box.label(text="No UV data loaded")
            return

        box.label(
            text=f"Object: {state.object_name}"
        )

        box.label(
            text=f"Vertices: {state.vertex_count}"
        )

        box.label(
            text=f"Edges: {state.edge_count}"
        )

        box.label(
            text=f"Faces: {state.face_count}"
        )

        box.label(
            text=f"UV Layer: {state.uv_layer_name}"
        )

        box.label(
            text=f"UV Loops: {state.uv_loop_count}"
        )

        box.separator()

        box.label(
            text=(
                f"UV Islands: "
                f"{state.uv_island_count}"
            ),
            icon="GROUP_UVS",
        )

        box.label(
            text=(
                "UV Boundary Edges: "
                f"{state.uv_boundary_edge_count}"
            ),
            icon="EDGESEL",
        )

        box.separator()

        box.label(
            text=(
                "Closed Boundary Loops: "
                f"{state.uv_closed_loop_count}"
            ),
            icon="EDGESEL",
        )

        box.label(
            text=(
                "Open Boundary Chains: "
                f"{state.uv_open_chain_count}"
            ),
        )
        box.label(
            text=(
                "Ordered Boundary Loops: "
                f"{state.uv_ordered_loop_count}"
            ),
            icon="EDGESEL",
        )

        box.label(
            text=(
                "Failed Loop Orders: "
                f"{state.uv_failed_loop_order_count}"
            ),
        )
        box.separator()

        box.label(
            text=(
                "Detected Corners: "
                f"{state.uv_detected_corner_count}"
            ),
            icon="VERTEXSEL",
        )

        box.label(
            text=(
                "Loops With Corners: "
                f"{state.uv_loops_with_corners}"
            ),
        )

        box.label(
            text=(
                "Loops Without Corners: "
                f"{state.uv_loops_without_corners}"
            ),
        )

        box.label(
            text=(
                "Most Corners In Loop: "
                f"{state.uv_maximum_corner_count}"
            ),
        )

        box.label(
            text=(
                "Fewest Corners In Loop: "
                f"{state.uv_minimum_corner_count}"
            ),
        )

        box.label(
            text=(
                "Largest Loop: "
                f"{state.largest_loop_edge_count} "
                "edges"
            ),
        )

        box.label(
            text=(
                "Smallest Loop: "
                f"{state.smallest_loop_edge_count} "
                "edges"
            ),
        )


classes = (
    ZPTOPO_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)