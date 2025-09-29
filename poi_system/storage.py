import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from .model import POIType, POI, Visitor, Visit
from .exceptions import POIError
from .utils import distance, feq, fle, EPSILON, in_bounds

class POIRegistry:

    def __init__(self, epsilon: float = EPSILON):
        self.epsilon = float(epsilon)
        self.poi_types: Dict[str, POIType] = {}
        self.pois: Dict[int, POI] = {}
        self.used_poi_ids: set[int] = set()  # "never reused" history
        self.visitors: Dict[int, Visitor] = {}
        # if key doesn't exist, WHO CARES?????? just return empty list
        self.visits_by_visitor: Dict[int, List[Visit]] = defaultdict(list)

    def add_poi_type(self, name: str, attributes: Optional[List[str]] = None):
        if not name or not name.strip():
            raise POIError("Type name cannot be empty.")
        if name in self.poi_types:
            raise POIError(f"Type '{name}' already exists.")
        attrs = []
        if attributes:
            seen = set()
            for a in attributes:
                if a in seen:
                    continue
                seen.add(a)
                attrs.append(a)
        self.poi_types[name] = POIType(name=name, attributes=attrs)

    def delete_poi_type(self, name: str):
        if name not in self.poi_types:
            raise POIError(f"Type '{name}' does not exist.")

        # Constraint: delete only if no POIs of that type exist
        for p in self.pois.values():
            if p.type_name == name:
                raise POIError(f"Cannot delete type '{name}': there are existing POIs of this type.")

        del self.poi_types[name]

    def add_attribute(self, type_name: str, attr: str):
        t = self._require_type(type_name)
        if attr in t.attributes:
            return
        t.attributes.append(attr)

        # Existing POIs of this type get None for the new attribute
        for poi in self.pois.values():
            if poi.type_name == type_name:
                poi.attributes.setdefault(attr, None)

    def delete_attribute(self, type_name: str, attr: str):
        t = self._require_type(type_name)
        if attr not in t.attributes:
            return
        t.attributes.remove(attr)

        # Remove attribute from existing POIs
        for poi in self.pois.values():
            if poi.type_name == type_name:
                poi.attributes.pop(attr, None)

    # Optional extension
    def rename_attribute(self, type_name: str, old: str, new: str):
        t = self._require_type(type_name)

        if old not in t.attributes:
            raise POIError(f"Attribute '{old}' not found in type '{type_name}'.")
        if new in t.attributes:
            raise POIError(f"Attribute '{new}' already exists in type '{type_name}'.")

        # rename in schema
        idx = t.attributes.index(old)
        t.attributes[idx] = new

        # migrate all POIs
        for poi in self.pois.values():
            if poi.type_name == type_name:
                if old in poi.attributes:
                    poi.attributes[new] = poi.attributes.pop(old)
                else:
                    poi.attributes.setdefault(new, None)

    # Optional extension
    def rename_type(self, old: str, new: str):
        if old not in self.poi_types:
            raise POIError(f"Type '{old}' not found.")
        if new in self.poi_types:
            raise POIError(f"Type '{new}' already exists.")
        t = self.poi_types.pop(old)

        self.poi_types[new] = POIType(name=new, attributes=list(t.attributes))
        for poi in self.pois.values():
            if poi.type_name == old:
                poi.type_name = new

    def add_poi(self, id: int, name: str, type_name: str, x: int, y: int, attributes: Optional[Dict[str, object]] = None):
        if id in self.used_poi_ids:
            raise POIError(f"POI id {id} has been used before and cannot be reused.")
        if id in self.pois:
            raise POIError(f"POI id {id} already exists.")
        t = self._require_type(type_name)
        if not isinstance(x, int) or not isinstance(y, int) or not in_bounds(x,y):
            raise POIError("Coordinates must be integers within 0..999.")
        poi_attrs = {}
        if attributes:
            # only accept attributes defined by the type; others are ignored
            for k, v in attributes.items():
                if k in t.attributes:
                    poi_attrs[k] = v

        # fill missing attributes with None
        for a in t.attributes:
            poi_attrs.setdefault(a, None)

        self.pois[id] = POI(id=id, name=name, type_name=type_name, x=x, y=y, attributes=poi_attrs)
        self.used_poi_ids.add(id)

    def delete_poi(self, id: int):
        if id not in self.pois:
            raise POIError(f"POI id {id} not found.")
        del self.pois[id]
        # note: id remains in used_poi_ids and cannot be reused

    def add_visitor(self, id: int, name: str, nationality: str):
        if id in self.visitors:
            raise POIError(f"Visitor id {id} already exists.")
        self.visitors[id] = Visitor(id=id, name=name, nationality=nationality)

    def add_visit(self, visitor_id: int, poi_id: int, date: str, rating: Optional[int] = None):
        if visitor_id not in self.visitors:
            raise POIError(f"Visitor {visitor_id} not found.")
        if poi_id not in self.pois:
            raise POIError(f"POI {poi_id} not found.")

        datetime.datetime.strptime(date, "%d/%m/%Y")
        if rating is not None:
            if not (isinstance(rating, int) and 1 <= rating <= 10):
                raise POIError("Rating must be integer 1..10 if provided.")
        self.visits_by_visitor[visitor_id].append(Visit(visitor_id=visitor_id, poi_id=poi_id, date=date, rating=rating))

    def list_pois_by_type(self, type_name: str) -> List[Tuple[int, str, Tuple[int,int], Dict[str,object]]]:
        self._require_type(type_name)
        out = []
        for p in self.pois.values():
            if p.type_name == type_name:
                out.append((p.id, p.name, (p.x, p.y), dict(p.attributes)))

        out.sort(key=lambda x: (x[0], x[1]))
        return out

    def closest_pair(self):
        items = list(self.pois.values())

        if len(items) < 2:
            return None

        best = None

        for i in range(len(items)):
            for j in range(i+1, len(items)):
                p1, p2 = items[i], items[j]
                d = distance((p1.x,p1.y), (p2.x,p2.y))
                if best is None or d < best[2] - self.epsilon or (feq(d, best[2], self.epsilon) and (min(p1.id,p2.id),max(p1.id,p2.id)) < (min(best[0].id,best[1].id),max(best[0].id,best[1].id))):
                    best = (p1, p2, d)

        p1, p2, dist = best

        return ((p1.id, p1.name, (p1.x,p1.y)), (p2.id, p2.name, (p2.x,p2.y)), dist)

    def count_pois_per_type(self) -> List[Tuple[str,int]]:
        counts = {t:0 for t in self.poi_types}

        for p in self.pois.values():
            counts[p.type_name] = counts.get(p.type_name, 0) + 1

        out = list(counts.items())
        out.sort(key=lambda x: (x[0]))  # alphabetical by type
        return out

    def pois_within_radius(self, c0: Tuple[int,int], r: float) -> List[Tuple[int,str,Tuple[int,int],str,float]]:
        x0, y0 = c0

        if not in_bounds(int(x0), int(y0)):
            raise POIError("c0 must be within 0..999.")

        out = []
        for p in self.pois.values():
            d = distance((x0,y0),(p.x,p.y))
            if fle(d, r, self.epsilon):
                out.append((p.id, p.name, (p.x,p.y), p.type_name, d))

        out.sort(key=lambda x: (x[4], x[0], x[1]))  # by distance, then id, then name

        return out

    def k_closest(self, c0: Tuple[int,int], k: int) -> List[Tuple[int,str,Tuple[int,int],str,float]]:
        x0,y0 = c0
        if not in_bounds(int(x0), int(y0)):
            raise POIError("c0 must be within 0..999.")
        arr = []
        for p in self.pois.values():
            d = distance((x0,y0),(p.x,p.y))
            arr.append((p.id, p.name, (p.x,p.y), p.type_name, d))
        arr.sort(key=lambda x: (x[4], x[0], x[1]))
        return arr[:max(0,k)]

    def at_exact_radius(self, c0: Tuple[int, int], r: float) \
        -> List[Tuple[int, str, Tuple[int, int], str, float]]:
        x0, y0 = c0
        if not in_bounds(int(x0), int(y0)):
            raise POIError("c0 must be within 0..999.")

        out = []

        for p in self.pois.values():
            d = distance((x0, y0),(p.x, p.y))
            if feq(d, r, self.epsilon):
                out.append((p.id, p.name, (p.x, p.y), p.type_name, d))

        out.sort(key=lambda x: (x[4], x[0], x[1]))
        return out

    def visits_for_visitor(self, visitor_id: int) -> List[Tuple[int, str, str]]:
        if visitor_id not in self.visitors:
            raise POIError(f"Visitor {visitor_id} not found.")

        out = []
        for v in self.visits_by_visitor.get(visitor_id, []):
            poi = self.pois.get(v.poi_id)
            if poi:
                out.append((poi.id, poi.name, v.date))

        # by poi id then name then date
        out.sort(key=lambda x: (x[0], x[1], x[2]))
        return out

    def number_of_visitors_per_poi(self) -> List[Tuple[int, int]]:
        visitor_sets = defaultdict(set)

        for vid, visits in self.visits_by_visitor.items():
            for v in visits:
                visitor_sets[v.poi_id].add(vid)

        out = [(pid, len(visitor_sets.get(pid,set()))) for pid in self.pois]
        out.sort(key=lambda x: (x[0]))  # by poi id
        return out

    def number_of_pois_per_visitor(self) -> List[Tuple[int, int]]:
        poi_sets = defaultdict(set)
        for vid, visits in self.visits_by_visitor.items():
            for v in visits:
                poi_sets[vid].add(v.poi_id)

        out = [(vid, len(poi_sets.get(vid,set()))) for vid in self.visitors]
        out.sort(key=lambda x: (x[0]))  # by visitor id
        return out

    def top_k_visitors_by_poi_count(self, k: int) -> List[Tuple[int, str, int]]:
        counts = defaultdict(set)
        for vid, visits in self.visits_by_visitor.items():
            for v in visits:
                counts[vid].add(v.poi_id)

        items = []

        for vid, vis in self.visitors.items():
            c = len(counts.get(vid, set()))
            items.append((vid, vis.name, c))

        items.sort(key=lambda x: (-x[2], x[0], x[1]))
        return items[:max(0,k)]

    def top_k_pois_by_visitor_count(self, k: int) -> List[Tuple[int, str, int]]:
        visitor_sets = defaultdict(set)

        for vid, visits in self.visits_by_visitor.items():
            for v in visits:
                visitor_sets[v.poi_id].add(vid)

        items = []

        for pid, poi in self.pois.items():
            c = len(visitor_sets.get(pid, set()))
            items.append((pid, poi.name, c))

        items.sort(key=lambda x: (-x[2], x[0], x[1]))
        return items[:max(0,k)]

    def coverage_fairness(self, m: int, t: int) -> List[Tuple[int, str, str, int, int]]:
        poi_sets = defaultdict(set)
        type_sets = defaultdict(set)

        for vid, visits in self.visits_by_visitor.items():
            for v in visits:
                poi_sets[vid].add(v.poi_id)
                poi = self.pois.get(v.poi_id)
                if poi:
                    type_sets[vid].add(poi.type_name)

        out = []

        for vid, visitor in self.visitors.items():
            np = len(poi_sets.get(vid,set()))
            nt = len(type_sets.get(vid,set()))
            if np >= m and nt >= t:
                out.append((vid, visitor.name, visitor.nationality, np, nt))

        # by id then name
        out.sort(key=lambda x: (x[0], x[1]))
        return out

    def _require_type(self, name: str) -> POIType:
        if name not in self.poi_types:
            raise POIError(f"Type '{name}' not found.")
        return self.poi_types[name]
