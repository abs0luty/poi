from math import hypot
from typing import Tuple

GRID_MIN = 0
GRID_MAX = 999
GRID_SIZE = 1000

# Floating point tolerance
EPSILON: float = 1e-6

def distance(p1: Tuple[int,int], p2: Tuple[int,int]) -> float:
    """Euclidean distance between two integer grid points."""
    return hypot(p1[0]-p2[0], p1[1]-p2[1])

def feq(a: float, b: float, eps: float = EPSILON) -> bool:
    """Floating-point equality with epsilon tolerance."""
    return abs(a - b) <= eps

def fle(a: float, b: float, eps: float = EPSILON) -> bool:
    """Floating-point <= with epsilon (i.e., a <= b + eps)."""
    return a <= b + eps

def in_bounds(x: int, y: int) -> bool:
    return (GRID_MIN <= x <= GRID_MAX) and (GRID_MIN <= y <= GRID_MAX)
