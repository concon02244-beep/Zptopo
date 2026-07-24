"""
UV boundary corner-detection algorithms for Zptopo.
"""

import math


def _cyclic_index_distance(index_a, index_b, point_count):
    """
    닫힌 루프에서 두 인덱스 사이의 가장 짧은 거리를 반환한다.
    """
    direct_distance = abs(index_a - index_b)

    return min(
        direct_distance,
        point_count - direct_distance,
    )


def _turn_angle_degrees(previous_point, point, next_point):
    """
    세 UV 점을 이용해 현재 점에서의 진행 방향 변화량을 계산한다.

    직선에 가까우면 0도,
    직각으로 꺾이면 약 90도에 가까운 값이 나온다.
    """
    incoming_x = point[0] - previous_point[0]
    incoming_y = point[1] - previous_point[1]

    outgoing_x = next_point[0] - point[0]
    outgoing_y = next_point[1] - point[1]

    incoming_length = math.hypot(
        incoming_x,
        incoming_y,
    )

    outgoing_length = math.hypot(
        outgoing_x,
        outgoing_y,
    )

    if incoming_length == 0 or outgoing_length == 0:
        return 0.0

    dot_product = (
        incoming_x * outgoing_x
        + incoming_y * outgoing_y
    )

    cosine = dot_product / (
        incoming_length * outgoing_length
    )

    # 부동소수점 오차로 acos 범위를 벗어나는 것을 방지한다.
    cosine = max(-1.0, min(1.0, cosine))

    return math.degrees(math.acos(cosine))


def detect_ordered_loop_corners(
    ordered_loop,
    angle_threshold_degrees=35.0,
):
    """
    하나의 정렬된 닫힌 UV 루프에서 코너 후보를 찾는다.

    긴 하이폴리곤 경계에서는 바로 옆 점이 아니라
    여러 점 떨어진 위치를 비교해 작은 노이즈를 줄인다.
    """
    ordered_points = ordered_loop["ordered_points"]

    # 마지막 점은 시작점의 반복이므로 제외한다.
    points = ordered_points[:-1]
    point_count = len(points)

    if point_count < 3:
        return {
            "corner_indices": [],
            "corner_angles": [],
            "sample_window": 0,
        }

    # 루프가 길수록 더 넓은 범위로 방향 변화를 측정한다.
    sample_window = max(
        1,
        min(
            8,
            point_count // 20,
        ),
    )

    corner_candidates = []

    for point_index in range(point_count):
        previous_index = (
            point_index - sample_window
        ) % point_count

        next_index = (
            point_index + sample_window
        ) % point_count

        angle = _turn_angle_degrees(
            points[previous_index],
            points[point_index],
            points[next_index],
        )

        if angle < angle_threshold_degrees:
            continue

        corner_candidates.append(
            {
                "point_index": point_index,
                "angle": angle,
            }
        )

    # 둥글게 꺾인 한 구간에서 여러 점이 동시에 검출되는 것을
    # 줄이기 위해 강한 코너부터 선택한다.
    minimum_spacing = max(
        1,
        min(
            12,
            point_count // 40,
        ),
    )

    selected_candidates = []

    for candidate in sorted(
        corner_candidates,
        key=lambda item: item["angle"],
        reverse=True,
    ):
        is_too_close = any(
            _cyclic_index_distance(
                candidate["point_index"],
                selected["point_index"],
                point_count,
            ) <= minimum_spacing
            for selected in selected_candidates
        )

        if is_too_close:
            continue

        selected_candidates.append(candidate)

    # 루프를 도는 순서대로 다시 정렬한다.
    selected_candidates.sort(
        key=lambda item: item["point_index"]
    )

    return {
        "corner_indices": [
            candidate["point_index"]
            for candidate in selected_candidates
        ],
        "corner_angles": [
            candidate["angle"]
            for candidate in selected_candidates
        ],
        "sample_window": sample_window,
    }


def analyze_ordered_loop_corners(
    ordered_loops,
    angle_threshold_degrees=35.0,
):
    """
    모든 정렬된 경계 루프의 코너 통계를 반환한다.
    """
    loop_results = []

    for ordered_loop in ordered_loops:
        corner_result = detect_ordered_loop_corners(
            ordered_loop,
            angle_threshold_degrees,
        )

        loop_results.append(
            {
                "island_index": ordered_loop[
                    "island_index"
                ],
                "edge_count": ordered_loop[
                    "edge_count"
                ],
                "corner_indices": corner_result[
                    "corner_indices"
                ],
                "corner_angles": corner_result[
                    "corner_angles"
                ],
                "sample_window": corner_result[
                    "sample_window"
                ],
                "corner_count": len(
                    corner_result["corner_indices"]
                ),
            }
        )

    corner_counts = [
        result["corner_count"]
        for result in loop_results
    ]

    total_corner_count = sum(corner_counts)

    loops_with_corners = sum(
        1
        for corner_count in corner_counts
        if corner_count > 0
    )

    loops_without_corners = (
        len(loop_results) - loops_with_corners
    )

    return {
        "loop_results": loop_results,
        "total_corner_count": total_corner_count,
        "loops_with_corners": loops_with_corners,
        "loops_without_corners": loops_without_corners,
        "maximum_corner_count": (
            max(corner_counts)
            if corner_counts
            else 0
        ),
        "minimum_corner_count": (
            min(corner_counts)
            if corner_counts
            else 0
        ),
    }