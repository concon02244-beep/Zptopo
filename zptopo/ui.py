import bpy


class ZPTOPO_PT_main_panel(bpy.types.Panel):
    bl_label = "Zptopo"
    bl_idname = "ZPTOPO_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Zptopo"

    def draw(self, context):
        layout = self.layout

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


classes = (
    ZPTOPO_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)