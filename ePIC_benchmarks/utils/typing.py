from typing import Protocol

class Printable(Protocol):

    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        ...