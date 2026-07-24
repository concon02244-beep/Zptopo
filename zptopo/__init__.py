bl_info = {
    "name": "Zptopo",
    "author": "concon02244-beep",
    "version": (0, 7, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Zptopo",
    "description": "Garment retopology tools for Blender",
    "category": "Mesh",
}


from . import operators
from . import properties
from . import ui


modules = (
    properties,
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