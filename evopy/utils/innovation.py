"""Centralized tracking of NEAT innovation numbers."""

from __future__ import annotations

from typing import Dict, Tuple


class InnovationTracker:
    """Assigns deterministic innovation numbers for nodes and connections."""

    def __init__(self) -> None:
        self.reset()

    def reset(self, next_node_id: int = 0, next_connection_id: int = 0) -> None:
        self._connection_ids: Dict[Tuple[int, int], int] = {}
        self._split_node_ids: Dict[Tuple[int, int], int] = {}
        self._next_node_id: int = next_node_id
        self._next_connection_id: int = next_connection_id

    def sync_node_counter(self, next_node_id: int) -> None:
        self._next_node_id = max(self._next_node_id, next_node_id)

    def sync_connection_counter(self, next_connection_id: int) -> None:
        self._next_connection_id = max(self._next_connection_id, next_connection_id)

    @property
    def next_node_id(self) -> int:
        return self._next_node_id

    @property
    def next_connection_id(self) -> int:
        return self._next_connection_id

    def get_connection_id(self, in_node_id: int, out_node_id: int) -> int:
        key = self._normalize_key(in_node_id, out_node_id)
        if key not in self._connection_ids:
            self._connection_ids[key] = self._next_connection_id
            self._next_connection_id += 1
        return self._connection_ids[key]

    def get_split_node_id(self, in_node_id: int, out_node_id: int) -> int:
        key = self._normalize_key(in_node_id, out_node_id)
        if key not in self._split_node_ids:
            self._split_node_ids[key] = self._next_node_id
            self._next_node_id += 1
        return self._split_node_ids[key]

    @staticmethod
    def _normalize_key(in_node_id: int, out_node_id: int) -> Tuple[int, int]:
        return int(in_node_id), int(out_node_id)
