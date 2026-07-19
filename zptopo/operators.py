import bpy


class ZPTOPO_OT_test(bpy.types.Operator):
    bl_idname = "zptopo.test"
    bl_label = "Test Zptopo"
    bl_description = "Check whether the Zptopo addon is working"
    bl_options = {"REGISTER"}

    def execute(self, context):
        self.report({"INFO"}, "Zptopo is working!")
        return {"FINISHED"}


classes = (
    ZPTOPO_OT_test,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)