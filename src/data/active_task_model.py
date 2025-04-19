from enum import Enum

from attr import define


@define
class ActiveTaskModel:
    """Active task model."""
    title: str
    date: str
    color: str
    tags: tuple[str, ...]
    column: str


class ActiveTaskColumns(Enum):
    """Valid task columns."""
    DAY_WORK_GREAT = "6616e230658e744f56832163"
    DAY_WORK_AMAZING = "6616e235658e744f56832168"
    DAY_PERSONAL_GREAT = "6616e224658e744f56832157"
    DAY_PERSONAL_AMAZING = "6616e22a658e744f5683215c"
    WEEK_WORK_GREAT = "61c62f41824afc6c76352403"
    WEEK_WORK_AMAZING = "61c62f4d824afc6c76352419"
    WEEK_PERSONAL_GREAT = "61c62f26824afc6c763523ec"
    WEEK_PERSONAL_AMAZING = "661d365e658e7453a070c132"

    @classmethod
    def get_column_ids(cls):
        return tuple(item.value for item in cls)
