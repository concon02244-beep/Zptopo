import bpy


def get_uv_info(context):
    obj = context.active_object

    if obj is None:
        raise ValueError("활성 오브젝트가 없습니다.")

    if obj.type != "MESH":
        raise ValueError("선택한 오브젝트가 메쉬가 아닙니다.")

    mesh = obj.data

    if not mesh.uv_layers:
        raise ValueError("선택한 메쉬에 UV 맵이 없습니다.")

    active_uv = mesh.uv_layers.active

    return {
        "object_name": obj.name,
        "vertex_count": len(mesh.vertices),
        "edge_count": len(mesh.edges),
        "face_count": len(mesh.polygons),
        "uv_layer_name": active_uv.name,
        "uv_loop_count": len(active_uv.data),
    }