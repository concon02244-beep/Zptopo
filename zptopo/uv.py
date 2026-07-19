"""
Compatibility module for Zptopo UV tools.

The implementation lives in zptopo.engine.uv.
Existing imports from zptopo.uv remain compatible.
"""

from .engine.uv import (
    count_uv_boundary_edges,
    count_uv_islands,
    get_uv_boundary_loop_info,
    get_uv_boundary_mesh_edge_indices,
    get_uv_info,
)


__all__ = (
    "count_uv_boundary_edges",
    "count_uv_islands",
    "get_uv_boundary_loop_info",
    "get_uv_boundary_mesh_edge_indices",
    "get_uv_info",
)