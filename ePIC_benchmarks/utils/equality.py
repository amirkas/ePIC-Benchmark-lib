from typing import Sequence, Any, TypeVar, Hashable

T = TypeVar("T")

#Checks whether any 2 objects in a list are equal
def any_identical_objects(object_iterable : Sequence[T]) -> bool:

    #Tries to run faster algorithms for element equality checking
    if len(object_iterable) > 0:
        first_elem = object_iterable[0]

        #If the lists's element type is hashable, run the fastest method ( O(n) )
        #for checking if any 2 objects are identical
        if isinstance(first_elem, Hashable):

            object_set = set(object_iterable)
            return len(object_set) != len(object_iterable)

        #If the list's element type has a less than, or greater than comparator
        #Run the second fastest method ( O(nlogn) ) for checking if any 2 objects are identical
        elif hasattr(first_elem, '__lt__'):

            sorted_iterable = sorted(object_iterable)
            for i in range(len(sorted_iterable) - 2):
                a = sorted_iterable[i]
                b = sorted_iterable[i + 1]
                if a == b:
                    return True
            return False

    #Run O(n^2) algorithm for 
    for i in range(len(object_iterable) - 1):
        for j in range(i + 1, len(object_iterable)):
            if object_iterable[i] == object_iterable[j]:
                return True
    return False