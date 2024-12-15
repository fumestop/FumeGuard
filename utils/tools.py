from __future__ import annotations

from typing import Union


def parse_cooldown(retry_after: Union[int, float]):
    retry_after = int(retry_after)

    hours, remainder = divmod(retry_after, 3600)
    minutes, seconds = divmod(remainder, 60)

    return minutes, seconds
