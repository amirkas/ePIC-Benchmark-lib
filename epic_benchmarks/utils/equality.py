from typing import Sequence, Any


def any_identical_objects(object_iterable : Sequence[Any]) -> bool:

    for i in range(len(object_iterable) - 1):
        for j in range(i + 1, len(object_iterable)):
            if object_iterable[i] == object_iterable[j]:
                return True
    return False