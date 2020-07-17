from typing import List


def gcd_multiple(numbers: List[int]) -> int:
    if not numbers:
        return 1
    if len(numbers) == 1:
        return numbers[0]
    gcd = gcd_two(numbers[0], numbers[1])
    for i in range(2, len(numbers)):
        gcd = gcd_two(gcd, numbers[i])
    return gcd


def gcd_two(x: int, y: int) -> int:
    while y:
        x, y = y, x % y
    return x
