from enum import Enum

from attr import define


@define
class ActiveTaskModel:
    """Active task model."""
    title: str
    date: str
    color: str
    column: str


class ActiveTaskColumns(Enum):
    """Valid task columns."""
    WORK_GREAT = "6616e230658e744f56832163"
    WORK_AMAZING = "6616e235658e744f56832168"
    PERSONAL_GREAT = "6616e224658e744f56832157"
    PERSONAL_AMAZING = "6616e22a658e744f5683215c"

    @classmethod
    def get_column_ids(cls):
        return tuple(item.value for item in cls)
