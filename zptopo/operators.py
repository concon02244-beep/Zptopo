import bpy

from .uv import (
    get_uv_boundary_mesh_edge_indices,
    get_uv_info,
)


class ZPTOPO_OT_test(bpy.types.Operator):
    bl_idname = "zptopo.test"
    bl_label = "Test Zptopo"
    bl_description = (
        "Check whether the Zptopo addon is working"
    )
    bl_options = {"REGISTER"}

    def execute(self, context):
        self.report(
            {"INFO"},
            "Zptopo is working!",
        )
        return {"FINISHED"}


class ZPTOPO_OT_read_uv(bpy.types.Operator):
    bl_idname = "zptopo.read_uv"
    bl_label = "Read UV"
    bl_description = (
        "Read UV information from the selected mesh"
    )
    bl_options = {"REGISTER"}

    def execute(self, context):
        try:
            info = get_uv_info(context)

        except ValueError as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        state = context.scene.zptopo_state

        state.object_name = info["object_name"]
        state.vertex_count = info["vertex_count"]
        state.edge_count = info["edge_count"]
        state.face_count = info["face_count"]

        state.uv_layer_name = info[
            "uv_layer_name"
        ]

        state.uv_loop_count = info[
            "uv_loop_count"
        ]

        state.uv_island_count = info[
            "uv_island_count"
        ]

        state.uv_boundary_edge_count = info[
            "uv_boundary_edge_count"
        ]

        state.uv_closed_loop_count = info[
            "uv_closed_loop_count"
        ]

        state.uv_open_chain_count = info[
            "uv_open_chain_count"
        ]
        state.uv_ordered_loop_count = info[
            "uv_ordered_loop_count"
        ]

        state.uv_failed_loop_order_count = info[
            "uv_failed_loop_order_count"
        ]

        state.largest_loop_edge_count = info[
            "largest_loop_edge_count"
        ]

        state.smallest_loop_edge_count = info[
            "smallest_loop_edge_count"
        ]

        self.report(
            {"INFO"},
            (
                f"{info['object_name']} | "
                f"Islands: {info['uv_island_count']} | "
                "Closed Loops: "
                f"{info['uv_closed_loop_count']} | "
                "Open Chains: "
                f"{info['uv_open_chain_count']}"
            ),
        )

        print("----- Zptopo UV Info -----")
        print(f"Object: {state.object_name}")
        print(f"Vertices: {state.vertex_count}")
        print(f"Edges: {state.edge_count}")
        print(f"Faces: {state.face_count}")
        print(f"UV Layer: {state.uv_layer_name}")
        print(f"UV Loops: {state.uv_loop_count}")
        print(f"UV Islands: {state.uv_island_count}")

        print(
            "UV Boundary Edges: "
            f"{state.uv_boundary_edge_count}"
        )

        print(
            "Closed Boundary Loops: "
            f"{state.uv_closed_loop_count}"
        )

        print(
            "Open Boundary Chains: "
            f"{state.uv_open_chain_count}"
        )
        print(
            "Ordered Boundary Loops: "
            f"{state.uv_ordered_loop_count}"
        )

        print(
            "Failed Loop Orders: "
            f"{state.uv_failed_loop_order_count}"
        )

        print(
            "Largest Loop: "
            f"{state.largest_loop_edge_count} edges"
        )

        print(
            "Smallest Loop: "
            f"{state.smallest_loop_edge_count} edges"
        )

        print("--------------------------")

        return {"FINISHED"}


class ZPTOPO_OT_select_uv_boundary_edges(
    bpy.types.Operator
):
    bl_idname = (
        "zptopo.select_uv_boundary_edges"
    )
    bl_label = "Select UV Boundary Edges"

    bl_description = (
        "Select mesh edges that form UV island "
        "boundaries"
    )

    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object

        try:
            boundary_edge_indices = (
                get_uv_boundary_mesh_edge_indices(
                    context
                )
            )

        except ValueError as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        if not boundary_edge_indices:
            self.report(
                {"WARNING"},
                "UV 경계 엣지를 찾지 못했습니다.",
            )
            return {"CANCELLED"}

        if obj.mode != "OBJECT":
            bpy.ops.object.mode_set(
                mode="OBJECT"
            )

        mesh = obj.data

        for vertex in mesh.vertices:
            vertex.select = False

        for edge in mesh.edges:
            edge.select = False

        for polygon in mesh.polygons:
            polygon.select = False

        for edge_index in boundary_edge_indices:
            if edge_index < len(mesh.edges):
                mesh.edges[
                    edge_index
                ].select = True

        mesh.update()

        context.tool_settings.mesh_select_mode = (
            False,
            True,
            False,
        )

        bpy.ops.object.mode_set(mode="EDIT")

        self.report(
            {"INFO"},
            (
                "Selected "
                f"{len(boundary_edge_indices)} "
                "mesh boundary edges"
            ),
        )

        return {"FINISHED"}


classes = (
    ZPTOPO_OT_test,
    ZPTOPO_OT_read_uv,
    ZPTOPO_OT_select_uv_boundary_edges,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)