from functools import lru_cache


#["l1", "l2", "l3"]
#["p1", "p2", "p3"]
#["l1", "p1", "l2", "p2", "l3", "p3"]
def transform_payload(list1: list[str], list2: list[str]) -> str:
    return _transform_payload(tuple(list1), tuple(list2))


@lru_cache(maxsize=None)
def _transform_payload(list1: tuple[str, ...], list2: tuple[str, ...]) -> str:
    output = []

    for item1 in list1:
        output.append(item1)
        output.append(list2[list1.index(item1)])

    return ",".join(map(str, output))