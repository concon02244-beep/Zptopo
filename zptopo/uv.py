def _uvs_match(uv_a, uv_b, tolerance=0.000001):
    """두 UV 좌표가 허용 오차 안에서 같은지 확인한다."""
    return (
        abs(uv_a[0] - uv_b[0]) <= tolerance
        and abs(uv_a[1] - uv_b[1]) <= tolerance
    )


def count_uv_islands(mesh, uv_layer, tolerance=0.000001):
    """
    UV가 끊기지 않은 면들을 하나의 그룹으로 묶어
    UV 아일랜드 개수를 반환한다.
    """

    face_neighbors = {
        polygon.index: set()
        for polygon in mesh.polygons
    }

    edge_uv_data = {}

    for polygon in mesh.polygons:
        loop_indices = list(polygon.loop_indices)
        loop_count = len(loop_indices)

        for position, loop_index in enumerate(loop_indices):
            next_loop_index = loop_indices[(position + 1) % loop_count]

            vertex_a = mesh.loops[loop_index].vertex_index
            vertex_b = mesh.loops[next_loop_index].vertex_index

            uv_a = tuple(uv_layer.data[loop_index].uv)
            uv_b = tuple(uv_layer.data[next_loop_index].uv)

            edge_key = tuple(sorted((vertex_a, vertex_b)))

            uv_by_vertex = {
                vertex_a: uv_a,
                vertex_b: uv_b,
            }

            edge_uv_data.setdefault(edge_key, []).append(
                {
                    "face_index": polygon.index,
                    "uv_by_vertex": uv_by_vertex,
                }
            )

    for edge_key, connected_faces in edge_uv_data.items():
        if len(connected_faces) < 2:
            continue

        vertex_a, vertex_b = edge_key

        for first_index in range(len(connected_faces)):
            first = connected_faces[first_index]

            for second_index in range(
                first_index + 1,
                len(connected_faces),
            ):
                second = connected_faces[second_index]

                first_uv_a = first["uv_by_vertex"][vertex_a]
                first_uv_b = first["uv_by_vertex"][vertex_b]

                second_uv_a = second["uv_by_vertex"][vertex_a]
                second_uv_b = second["uv_by_vertex"][vertex_b]

                edge_is_continuous = (
                    _uvs_match(
                        first_uv_a,
                        second_uv_a,
                        tolerance,
                    )
                    and _uvs_match(
                        first_uv_b,
                        second_uv_b,
                        tolerance,
                    )
                )

                if not edge_is_continuous:
                    continue

                first_face = first["face_index"]
                second_face = second["face_index"]

                face_neighbors[first_face].add(second_face)
                face_neighbors[second_face].add(first_face)

    visited_faces = set()
    island_count = 0

    for polygon in mesh.polygons:
        start_face = polygon.index

        if start_face in visited_faces:
            continue

        island_count += 1
        stack = [start_face]

        while stack:
            current_face = stack.pop()

            if current_face in visited_faces:
                continue

            visited_faces.add(current_face)

            for neighbor in face_neighbors[current_face]:
                if neighbor not in visited_faces:
                    stack.append(neighbor)

    return island_count


def get_uv_info(context):
    obj = context.active_object

    if obj is None:
        raise ValueError("활성 오브젝트가 없습니다.")

    if obj.type != "MESH":
        raise ValueError("선택한 오브젝트가 메쉬가 아닙니다.")

    if obj.mode == "EDIT":
        obj.update_from_editmode()

    mesh = obj.data

    if not mesh.polygons:
        raise ValueError("선택한 메쉬에 면이 없습니다.")

    if not mesh.uv_layers:
        raise ValueError("선택한 메쉬에 UV 맵이 없습니다.")

    active_uv = mesh.uv_layers.active

    if active_uv is None:
        raise ValueError("활성 UV 맵이 없습니다.")

    island_count = count_uv_islands(
        mesh,
        active_uv,
    )

    return {
        "object_name": obj.name,
        "vertex_count": len(mesh.vertices),
        "edge_count": len(mesh.edges),
        "face_count": len(mesh.polygons),
        "uv_layer_name": active_uv.name,
        "uv_loop_count": len(active_uv.data),
        "uv_island_count": island_count,
    }