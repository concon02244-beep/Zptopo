import bpy

from .uv import get_uv_info


class ZPTOPO_OT_test(bpy.types.Operator):
    bl_idname = "zptopo.test"
    bl_label = "Test Zptopo"
    bl_description = "Check whether the Zptopo addon is working"
    bl_options = {"REGISTER"}

    def execute(self, context):
        self.report({"INFO"}, "Zptopo is working!")
        return {"FINISHED"}


class ZPTOPO_OT_read_uv(bpy.types.Operator):
    bl_idname = "zptopo.read_uv"
    bl_label = "Read UV"
    bl_description = "Read UV information from the selected mesh"
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
        state.uv_layer_name = info["uv_layer_name"]
        state.uv_loop_count = info["uv_loop_count"]
        state.uv_island_count = info["uv_island_count"]

        self.report(
            {"INFO"},
            (
                f"{info['object_name']} | "
                f"UV Islands: {info['uv_island_count']}"
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
        print("--------------------------")

        return {"FINISHED"}


classes = (
    ZPTOPO_OT_test,
    ZPTOPO_OT_read_uv,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)