bl_info = {
    "name": "Zptopo",
    "author": "concon02244-beep",
    "version": (0, 1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Zptopo",
    "description": "Garment retopology tools for Blender",
    "category": "Mesh",
}


from . import operators
from . import ui


modules = (
    operators,
    ui,
)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()


if __name__ == "__main__":
    register()