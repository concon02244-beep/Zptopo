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

        layout.separator()

        box = layout.box()
        box.label(text="UV Information", icon="GROUP_UVS")

        if not state.object_name:
            box.label(text="No UV data loaded")
            return

        box.label(text=f"Object: {state.object_name}")
        box.label(text=f"Vertices: {state.vertex_count}")
        box.label(text=f"Edges: {state.edge_count}")
        box.label(text=f"Faces: {state.face_count}")
        box.label(text=f"UV Layer: {state.uv_layer_name}")
        box.label(text=f"UV Loops: {state.uv_loop_count}")


classes = (
    ZPTOPO_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)