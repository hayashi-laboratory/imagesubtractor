from typing import NamedTuple, Optional

from numpy import ndarray

__all__ = ["Task", "Result"]


class Task(NamedTuple):
    num: Optional[int] = None
    file1: Optional[str] = None
    file2: Optional[str] = None


class Result(NamedTuple):
    num: Optional[int] = None
    image: Optional[ndarray] = None
    data: Optional[ndarray] = None

