from dataclasses import dataclass, field
from typing import Dict, List, Optional 

from .utils import in_bounds

@dataclass(frozen=True)
class POIType:
    name: str
    attributes: List[str] = field(default_factory=list)

@dataclass
class POI:
    id: int
    name: str
    type_name: str
    x: int
    y: int
    attributes: Dict[str, object] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.x, int) or not isinstance(self.y, int):
            raise ValueError("Coordinates must be integers.")

        if not in_bounds(self.x, self.y):
            raise ValueError(f"Coordinates must be within 0..999 inclusive: got ({self.x},{self.y})")

@dataclass
class Visitor:
    id: int
    name: str
    nationality: str

@dataclass(frozen=True)
class Visit:
    visitor_id: int
    poi_id: int
    date: str  # dd/mm/yyyy
    rating: Optional[int] = None
