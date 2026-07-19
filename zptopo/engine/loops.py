"""
Boundary-loop ordering algorithms for Zptopo.
"""


def _other_point(segment, current_point):
    """
    선분의 양 끝점 중 current_point가 아닌 반대쪽 점을 반환한다.
    """
    point_a = segment["point_a"]
    point_b = segment["point_b"]

    if current_point == point_a:
        return point_b

    if current_point == point_b:
        return point_a

    raise ValueError(
        "현재 점이 해당 경계 선분에 포함되어 있지 않습니다."
    )


def _order_closed_component(
    boundary_segments,
    component,
):
    """
    하나의 닫힌 경계 컴포넌트를 순서대로 정렬한다.

    반환값:
    {
        "island_index": int,
        "ordered_segment_indices": [...],
        "ordered_points": [...],
        "edge_count": int,
    }

    ordered_points에는 마지막에 시작점이 한 번 더 포함된다.
    """
    component_segment_indices = set(
        component["segment_indices"]
    )

    if not component["is_closed"]:
        raise ValueError(
            "닫히지 않은 경계 컴포넌트는 정렬할 수 없습니다."
        )

    point_to_segments = {}

    for segment_index in component_segment_indices:
        segment = boundary_segments[segment_index]

        point_to_segments.setdefault(
            segment["point_a"],
            [],
        ).append(segment_index)

        point_to_segments.setdefault(
            segment["point_b"],
            [],
        ).append(segment_index)

    # 정상적인 닫힌 루프라면 모든 점의 연결 차수가 2여야 한다.
    for connected_segments in point_to_segments.values():
        if len(connected_segments) != 2:
            raise ValueError(
                "경계 루프의 한 점에 연결된 선분 수가 2가 아닙니다."
            )

    # 실행할 때마다 같은 결과가 나오도록
    # UV 정수 좌표가 가장 작은 점을 시작점으로 정한다.
    start_point = min(point_to_segments.keys())

    start_candidates = point_to_segments[start_point]

    # 시작점에서 갈 수 있는 두 방향 중
    # 반대쪽 UV 좌표가 더 작은 방향을 우선한다.
    first_segment_index = min(
        start_candidates,
        key=lambda segment_index: _other_point(
            boundary_segments[segment_index],
            start_point,
        ),
    )

    ordered_segment_indices = []
    ordered_points = [start_point]

    visited_segments = set()
    current_point = start_point
    current_segment_index = first_segment_index

    while True:
        if current_segment_index in visited_segments:
            raise ValueError(
                "루프가 닫히기 전에 같은 선분을 다시 방문했습니다."
            )

        visited_segments.add(current_segment_index)
        ordered_segment_indices.append(
            current_segment_index
        )

        current_segment = boundary_segments[
            current_segment_index
        ]

        next_point = _other_point(
            current_segment,
            current_point,
        )

        ordered_points.append(next_point)

        # 시작점으로 돌아오면 루프가 닫힌 것이다.
        if next_point == start_point:
            break

        next_candidates = [
            segment_index
            for segment_index in point_to_segments[
                next_point
            ]
            if segment_index not in visited_segments
        ]

        if len(next_candidates) != 1:
            raise ValueError(
                "다음 경계 선분을 하나로 결정할 수 없습니다."
            )

        current_point = next_point
        current_segment_index = next_candidates[0]

    if visited_segments != component_segment_indices:
        raise ValueError(
            "컴포넌트의 일부 선분이 정렬 결과에서 누락됐습니다."
        )

    if len(ordered_segment_indices) != component["edge_count"]:
        raise ValueError(
            "정렬된 선분 수가 컴포넌트 엣지 수와 다릅니다."
        )

    return {
        "island_index": component["island_index"],
        "ordered_segment_indices": ordered_segment_indices,
        "ordered_points": ordered_points,
        "edge_count": len(ordered_segment_indices),
    }


def order_boundary_components(
    boundary_segments,
    components,
):
    """
    닫힌 경계 컴포넌트를 모두 순서대로 정렬한다.

    정렬에 성공한 루프와 실패한 컴포넌트를 따로 반환한다.
    """
    ordered_loops = []
    failed_components = []

    for component in components:
        if not component["is_closed"]:
            continue

        try:
            ordered_loop = _order_closed_component(
                boundary_segments,
                component,
            )

        except ValueError as error:
            failed_components.append(
                {
                    "component": component,
                    "error": str(error),
                }
            )
            continue

        ordered_loops.append(ordered_loop)

    return ordered_loops, failed_components