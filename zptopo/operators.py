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

        message = (
            f"{info['object_name']} | "
            f"Vertices: {info['vertex_count']} | "
            f"Faces: {info['face_count']} | "
            f"UV: {info['uv_layer_name']}"
        )

        self.report({"INFO"}, message)

        print("----- Zptopo UV Info -----")
        print(f"Object: {info['object_name']}")
        print(f"Vertices: {info['vertex_count']}")
        print(f"Edges: {info['edge_count']}")
        print(f"Faces: {info['face_count']}")
        print(f"UV Layer: {info['uv_layer_name']}")
        print(f"UV Loops: {info['uv_loop_count']}")
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