def _uvs_match(uv_a, uv_b, tolerance=0.000001):
    """두 UV 좌표가 허용 오차 안에서 같은지 확인한다."""
    return (
        abs(uv_a[0] - uv_b[0]) <= tolerance
        and abs(uv_a[1] - uv_b[1]) <= tolerance
    )


def _quantize_uv(uv, tolerance=0.000001):
    """
    UV 좌표를 허용 오차 기준의 정수로 변환한다.

    같은 위치의 UV가 미세한 소수점 오차 때문에
    서로 다른 좌표로 판정되는 것을 방지한다.
    """
    return (
        round(uv[0] / tolerance),
        round(uv[1] / tolerance),
    )


def _collect_uv_edge_data(mesh, uv_layer):
    """
    각 폴리곤이 사용하는 메쉬 엣지와
    해당 엣지 양 끝의 UV 좌표를 수집한다.
    """
    edge_uv_data = {}

    for polygon in mesh.polygons:
        loop_indices = list(polygon.loop_indices)
        loop_count = len(loop_indices)

        for position, loop_index in enumerate(loop_indices):
            next_loop_index = loop_indices[
                (position + 1) % loop_count
            ]

            loop = mesh.loops[loop_index]
            next_loop = mesh.loops[next_loop_index]

            vertex_a = loop.vertex_index
            vertex_b = next_loop.vertex_index
            edge_index = loop.edge_index

            uv_a = tuple(uv_layer.data[loop_index].uv)
            uv_b = tuple(uv_layer.data[next_loop_index].uv)

            edge_key = tuple(sorted((vertex_a, vertex_b)))

            edge_uv_data.setdefault(edge_key, []).append(
                {
                    "face_index": polygon.index,
                    "edge_index": edge_index,
                    "uv_by_vertex": {
                        vertex_a: uv_a,
                        vertex_b: uv_b,
                    },
                }
            )

    return edge_uv_data


def count_uv_islands(
    mesh,
    uv_layer,
    edge_uv_data=None,
    tolerance=0.000001,
):
    """
    UV가 끊기지 않은 면들을 하나의 그룹으로 묶어
    UV 아일랜드 개수를 반환한다.
    """
    if edge_uv_data is None:
        edge_uv_data = _collect_uv_edge_data(
            mesh,
            uv_layer,
        )

    face_neighbors = {
        polygon.index: set()
        for polygon in mesh.polygons
    }

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


def _find_uv_boundary_data(
    edge_uv_data,
    tolerance=0.000001,
):
    """
    UV 경계 조각 수와 경계에 해당하는
    실제 메쉬 엣지 인덱스를 반환한다.
    """
    boundary_segment_count = 0
    boundary_mesh_edge_indices = set()

    for edge_key, edge_uses in edge_uv_data.items():
        vertex_a, vertex_b = edge_key
        uv_segment_uses = {}

        for edge_use in edge_uses:
            uv_a = edge_use["uv_by_vertex"][vertex_a]
            uv_b = edge_use["uv_by_vertex"][vertex_b]

            segment_key = (
                _quantize_uv(uv_a, tolerance),
                _quantize_uv(uv_b, tolerance),
            )

            uv_segment_uses.setdefault(
                segment_key,
                [],
            ).append(edge_use)

        for segment_uses in uv_segment_uses.values():
            if len(segment_uses) != 1:
                continue

            boundary_segment_count += 1

            boundary_mesh_edge_indices.add(
                segment_uses[0]["edge_index"]
            )

    return (
        boundary_segment_count,
        boundary_mesh_edge_indices,
    )


def count_uv_boundary_edges(
    edge_uv_data,
    tolerance=0.000001,
):
    """
    UV 공간에서 경계를 이루는 UV 엣지 조각 수를 반환한다.
    """
    boundary_count, _ = _find_uv_boundary_data(
        edge_uv_data,
        tolerance,
    )

    return boundary_count


def get_uv_boundary_mesh_edge_indices(
    context,
    tolerance=0.000001,
):
    """
    UV 경계에 해당하는 실제 Blender 메쉬 엣지의
    인덱스 집합을 반환한다.
    """
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

    edge_uv_data = _collect_uv_edge_data(
        mesh,
        active_uv,
    )

    _, boundary_mesh_edge_indices = _find_uv_boundary_data(
        edge_uv_data,
        tolerance,
    )

    return boundary_mesh_edge_indices


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

    edge_uv_data = _collect_uv_edge_data(
        mesh,
        active_uv,
    )

    island_count = count_uv_islands(
        mesh,
        active_uv,
        edge_uv_data=edge_uv_data,
    )

    boundary_edge_count = count_uv_boundary_edges(
        edge_uv_data,
    )

    return {
        "object_name": obj.name,
        "vertex_count": len(mesh.vertices),
        "edge_count": len(mesh.edges),
        "face_count": len(mesh.polygons),
        "uv_layer_name": active_uv.name,
        "uv_loop_count": len(active_uv.data),
        "uv_island_count": island_count,
        "uv_boundary_edge_count": boundary_edge_count,
    }