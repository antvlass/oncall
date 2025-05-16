from datetime import time
from enum import Enum


class Category(str, Enum):
    DIV1400 = "div1400"
    DIV900 = "div900"
    DIV600 = "div600"
    DIV350 = "div350"

    @classmethod
    def list(cls) -> list[str]:
        return list(cls)

    def get_divisor(self) -> int:
        return {
            Category.DIV1400: 1400,
            Category.DIV900: 900,
            Category.DIV600: 600,
            Category.DIV350: 350,
        }[self]


WORK_START = time(9, 0)
WORK_END = time(17, 0)
DIV900_START = time(18, 0)
DIV900_END = time(7, 0)
DIV350_START_TIME = time(7, 0)

DIV600_HOLIDAYS = {
    "Trettondedag jul",
    "Första maj",
    "Kristi himmelsfärdsdag",
    "Alla helgons dag",
    "Sveriges nationaldag",
}
