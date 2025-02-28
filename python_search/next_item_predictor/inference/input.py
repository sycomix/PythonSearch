from __future__ import annotations

import datetime
import os
from typing import Optional


class ModelInput:
    hour: int
    month: int
    previous_key: str
    previous_previous_key: str
    times_used_previous: int
    times_used_previous_previous: int

    def __init__(
        self,
        *,
        hour,
        month,
        previous_key: str,
        previous_previous_key: str,
        times_used_previous: Optional[int] = None,
        times_used_previous_previous: Optional[int] = None,
    ):
        self.hour = hour
        self.month = month
        if not previous_key:
            raise ValueError("Previous keys cannot be empty")

        if not previous_previous_key:
            raise ValueError("Previous previous keys cannot be empty")

        self.previous_key = previous_key
        self.previous_previous_key = previous_previous_key
        self.times_used_previous = times_used_previous
        self.times_used_previous_previous = times_used_previous_previous

    @staticmethod
    def with_given_keys(previous_key: str, previous_previous_key: str) -> "ModelInput":
        """
        Do inference based on the current time and the recent used keys
        """
        now = datetime.datetime.now()
        hour = int(os.environ["FORCE_HOUR"]) if "FORCE_HOUR" in os.environ else now.hour
        month = (
            int(os.environ["FORCE_MONTH"]) if "FORCE_MONTH" in os.environ else now.month
        )

        instance = ModelInput(
            hour=hour,
            month=month,
            previous_key=previous_key,
            previous_previous_key=previous_previous_key,
        )

        # logging.("Inference input: ", instance.__dict__)

        return instance
