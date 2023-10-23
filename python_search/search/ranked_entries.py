from __future__ import annotations

from typing import List, Tuple


class RankedEntries:
    type = List[Tuple[str, dict]]

    @staticmethod
    def get_list_of_tuples(from_keys: List[str], entities: dict) -> RankedEntries.type:
        return [
            (used_key, entities[used_key])
            for used_key in from_keys
            if used_key in entities
        ]
