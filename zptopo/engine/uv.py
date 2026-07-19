from .loops import order_boundary_components

def _uvs_match(uv_a, uv_b, tolerance=0.000001):
    """두 UV 좌표가 허용 오차 안에서 같은지 확인한다."""
    return (
        abs(uv_a[0] - uv_b[0]) <= tolerance
        and abs(uv_a[1] - uv_b[1]) <= tolerance
    )


def _quantize_uv(uv, tolerance=0.000001):
    """
    UV 좌표를 허용 오차 기준의 정수 좌표로 변환한다.

    미세한 부동소수점 오차 때문에 같은 UV 좌표가
    서로 다른 점으로 판정되는 것을 방지한다.
    """
    return (
        round(uv[0] / tolerance),
        round(uv[1] / tolerance),
    )


def _collect_uv_edge_data(mesh, uv_layer):
    """
    메쉬 엣지가 각 면에서 어떤 UV 선분으로 사용되는지 수집한다.
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


def _build_uv_face_neighbors(
    mesh,
    edge_uv_data,
    tolerance=0.000001,
):
    """
    UV가 실제로 이어진 면끼리 이웃 관계를 만든다.

    3D에서 같은 엣지를 공유하더라도 UV가 갈라져 있으면
    서로 다른 UV 아일랜드로 처리한다.
    """
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

    return face_neighbors


def _find_uv_face_islands(
    mesh,
    edge_uv_data,
    tolerance=0.000001,
):
    """
    UV 아일랜드별 면 목록과 각 면의 아일랜드 번호를 반환한다.
    """
    face_neighbors = _build_uv_face_neighbors(
        mesh,
        edge_uv_data,
        tolerance,
    )

    islands = []
    face_to_island = {}
    visited_faces = set()

    for polygon in mesh.polygons:
        start_face = polygon.index

        if start_face in visited_faces:
            continue

        island_index = len(islands)
        island_faces = set()
        stack = [start_face]

        while stack:
            current_face = stack.pop()

            if current_face in visited_faces:
                continue

            visited_faces.add(current_face)
            island_faces.add(current_face)
            face_to_island[current_face] = island_index

            for neighbor in face_neighbors[current_face]:
                if neighbor not in visited_faces:
                    stack.append(neighbor)

        islands.append(island_faces)

    return islands, face_to_island


def count_uv_islands(
    mesh,
    uv_layer,
    edge_uv_data=None,
    tolerance=0.000001,
):
    """UV 아일랜드 개수를 반환한다."""
    if edge_uv_data is None:
        edge_uv_data = _collect_uv_edge_data(
            mesh,
            uv_layer,
        )

    islands, _ = _find_uv_face_islands(
        mesh,
        edge_uv_data,
        tolerance,
    )

    return len(islands)


def _find_uv_boundary_segments(
    mesh,
    edge_uv_data,
    tolerance=0.000001,
):
    """
    UV 공간의 경계 선분들을 검출한다.

    각 선분에는 다음 정보가 포함된다.

    - 소속 UV 아일랜드
    - UV 시작점
    - UV 끝점
    - 대응하는 실제 메쉬 엣지
    """
    _, face_to_island = _find_uv_face_islands(
        mesh,
        edge_uv_data,
        tolerance,
    )

    boundary_segments = []

    for edge_key, edge_uses in edge_uv_data.items():
        vertex_a, vertex_b = edge_key
        uv_segment_uses = {}

        for edge_use in edge_uses:
            uv_a = edge_use["uv_by_vertex"][vertex_a]
            uv_b = edge_use["uv_by_vertex"][vertex_b]

            point_a = _quantize_uv(uv_a, tolerance)
            point_b = _quantize_uv(uv_b, tolerance)

            segment_key = (
                point_a,
                point_b,
            )

            uv_segment_uses.setdefault(
                segment_key,
                [],
            ).append(edge_use)

        for segment_key, segment_uses in (
            uv_segment_uses.items()
        ):
            # 같은 UV 선분을 두 면이 공유하면 내부 엣지다.
            if len(segment_uses) != 1:
                continue

            edge_use = segment_uses[0]
            face_index = edge_use["face_index"]

            boundary_segments.append(
                {
                    "island_index": face_to_island[
                        face_index
                    ],
                    "point_a": segment_key[0],
                    "point_b": segment_key[1],
                    "edge_index": edge_use["edge_index"],
                    "face_index": face_index,
                }
            )

    return boundary_segments


def _build_boundary_components(boundary_segments):
    """
    서로 연결된 UV 경계 선분을 하나의 컴포넌트로 묶는다.

    정상적인 닫힌 컴포넌트는 경계 루프이며,
    끝점이 존재하는 컴포넌트는 열린 체인이다.
    """
    segments_by_island = {}

    for segment_index, segment in enumerate(
        boundary_segments
    ):
        island_index = segment["island_index"]

        segments_by_island.setdefault(
            island_index,
            [],
        ).append(segment_index)

    components = []

    for island_index, island_segment_indices in (
        segments_by_island.items()
    ):
        point_to_segments = {}

        for segment_index in island_segment_indices:
            segment = boundary_segments[segment_index]

            point_to_segments.setdefault(
                segment["point_a"],
                set(),
            ).add(segment_index)

            point_to_segments.setdefault(
                segment["point_b"],
                set(),
            ).add(segment_index)

        unvisited_segments = set(island_segment_indices)

        while unvisited_segments:
            start_segment = next(iter(unvisited_segments))
            stack = [start_segment]

            component_segments = set()
            component_points = set()

            while stack:
                current_segment = stack.pop()

                if current_segment not in (
                    unvisited_segments
                ):
                    continue

                unvisited_segments.remove(
                    current_segment
                )
                component_segments.add(
                    current_segment
                )

                segment = boundary_segments[
                    current_segment
                ]

                for point in (
                    segment["point_a"],
                    segment["point_b"],
                ):
                    component_points.add(point)

                    for neighbor_segment in (
                        point_to_segments[point]
                    ):
                        if neighbor_segment in (
                            unvisited_segments
                        ):
                            stack.append(neighbor_segment)

            point_degrees = {
                point: 0
                for point in component_points
            }

            for segment_index in component_segments:
                segment = boundary_segments[
                    segment_index
                ]

                point_degrees[segment["point_a"]] += 1
                point_degrees[segment["point_b"]] += 1

            is_closed = (
                len(component_segments) >= 3
                and all(
                    degree == 2
                    for degree in point_degrees.values()
                )
            )

            components.append(
                {
                    "island_index": island_index,
                    "segment_indices": component_segments,
                    "edge_count": len(
                        component_segments
                    ),
                    "point_count": len(
                        component_points
                    ),
                    "is_closed": is_closed,
                }
            )

    return components


def get_uv_boundary_loop_info(
    mesh,
    uv_layer,
    edge_uv_data=None,
    tolerance=0.000001,
):
    """
    UV 경계 루프 통계를 반환한다.
    """
    if edge_uv_data is None:
        edge_uv_data = _collect_uv_edge_data(
            mesh,
            uv_layer,
        )

    boundary_segments = _find_uv_boundary_segments(
        mesh,
        edge_uv_data,
        tolerance,
    )

    components = _build_boundary_components(
        boundary_segments
    )
    
    ordered_loops, failed_loop_orders = order_boundary_components(
        boundary_segments,
        components,
    )

    closed_loops = [
        component
        for component in components
        if component["is_closed"]
    ]

    open_chains = [
        component
        for component in components
        if not component["is_closed"]
    ]

    loop_edge_counts = [
        component["edge_count"]
        for component in closed_loops
    ]

    largest_loop_edge_count = (
        max(loop_edge_counts)
        if loop_edge_counts
        else 0
    )

    smallest_loop_edge_count = (
        min(loop_edge_counts)
        if loop_edge_counts
        else 0
    )

    return {
        "boundary_segment_count": len(
            boundary_segments
        ),
        "closed_loop_count": len(closed_loops),
        "open_chain_count": len(open_chains),
        "ordered_loop_count": len(ordered_loops),
        "failed_loop_order_count": len(
            failed_loop_orders
        ),
        "largest_loop_edge_count": (
            largest_loop_edge_count
        ),
        "smallest_loop_edge_count": (
            smallest_loop_edge_count
        ),
    }


def count_uv_boundary_edges(
    mesh,
    edge_uv_data,
    tolerance=0.000001,
):
    """
    UV 공간의 경계 선분 개수를 반환한다.
    """
    boundary_segments = _find_uv_boundary_segments(
        mesh,
        edge_uv_data,
        tolerance,
    )

    return len(boundary_segments)


def get_uv_boundary_mesh_edge_indices(
    context,
    tolerance=0.000001,
):
    """
    UV 경계에 해당하는 실제 메쉬 엣지 인덱스를 반환한다.
    """
    obj = context.active_object

    if obj is None:
        raise ValueError("활성 오브젝트가 없습니다.")

    if obj.type != "MESH":
        raise ValueError(
            "선택한 오브젝트가 메쉬가 아닙니다."
        )

    if obj.mode == "EDIT":
        obj.update_from_editmode()

    mesh = obj.data

    if not mesh.polygons:
        raise ValueError(
            "선택한 메쉬에 면이 없습니다."
        )

    if not mesh.uv_layers:
        raise ValueError(
            "선택한 메쉬에 UV 맵이 없습니다."
        )

    active_uv = mesh.uv_layers.active

    if active_uv is None:
        raise ValueError(
            "활성 UV 맵이 없습니다."
        )

    edge_uv_data = _collect_uv_edge_data(
        mesh,
        active_uv,
    )

    boundary_segments = _find_uv_boundary_segments(
        mesh,
        edge_uv_data,
        tolerance,
    )

    return {
        segment["edge_index"]
        for segment in boundary_segments
    }


def get_uv_info(context):
    obj = context.active_object

    if obj is None:
        raise ValueError("활성 오브젝트가 없습니다.")

    if obj.type != "MESH":
        raise ValueError(
            "선택한 오브젝트가 메쉬가 아닙니다."
        )

    if obj.mode == "EDIT":
        obj.update_from_editmode()

    mesh = obj.data

    if not mesh.polygons:
        raise ValueError(
            "선택한 메쉬에 면이 없습니다."
        )

    if not mesh.uv_layers:
        raise ValueError(
            "선택한 메쉬에 UV 맵이 없습니다."
        )

    active_uv = mesh.uv_layers.active

    if active_uv is None:
        raise ValueError(
            "활성 UV 맵이 없습니다."
        )

    edge_uv_data = _collect_uv_edge_data(
        mesh,
        active_uv,
    )

    island_count = count_uv_islands(
        mesh,
        active_uv,
        edge_uv_data=edge_uv_data,
    )

    boundary_loop_info = (
        get_uv_boundary_loop_info(
            mesh,
            active_uv,
            edge_uv_data=edge_uv_data,
        )
    )

    return {
        "object_name": obj.name,
        "vertex_count": len(mesh.vertices),
        "edge_count": len(mesh.edges),
        "face_count": len(mesh.polygons),
        "uv_layer_name": active_uv.name,
        "uv_loop_count": len(active_uv.data),
        "uv_island_count": island_count,
        "uv_boundary_edge_count": (
            boundary_loop_info[
                "boundary_segment_count"
            ]
        ),
        "uv_closed_loop_count": (
            boundary_loop_info[
                "closed_loop_count"
            ]
        ),
                "uv_open_chain_count": (
            boundary_loop_info[
                "open_chain_count"
            ]
        ),

        "uv_ordered_loop_count": (
            boundary_loop_info[
                "ordered_loop_count"
            ]
        ),

        "uv_failed_loop_order_count": (
            boundary_loop_info[
                "failed_loop_order_count"
            ]
        ),
        "largest_loop_edge_count": (
            boundary_loop_info[
                "largest_loop_edge_count"
            ]
        ),
        "smallest_loop_edge_count": (
            boundary_loop_info[
                "smallest_loop_edge_count"
            ]
        ),
    }