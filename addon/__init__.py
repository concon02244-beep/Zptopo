bl_info = {
    "name": "Zptopo",
    "author": "Zptopo Project",
    "version": (0, 1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Zptopo",
    "description": "Automatic retopology tools for clothing",
    "category": "Mesh",
}


def register():
    print("Zptopo Loaded")


def unregister():
    print("Zptopo Unloaded")


if __name__ == "__main__":
    register()