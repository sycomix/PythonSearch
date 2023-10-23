from typing import List

from python_search.configuration.loader import ConfigurationLoader


class EntriesLoader:
    """Class to access the current existing key"""

    @staticmethod
    def load_all_keys() -> List[str]:
        keys = list(ConfigurationLoader().load_entries().keys())

        print(f"Loaded in total {len(keys)} keys")

        return keys
