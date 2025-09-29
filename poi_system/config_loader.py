from typing import Dict, List
from .exceptions import ConfigError
import yaml 
import json, os, datetime

def _parse_date(s: str) -> str:
    try:
        datetime.datetime.strptime(s, "%d/%m/%Y")
        return s
    except Exception as e:
        raise ConfigError(f"Invalid date format (expected dd/mm/yyyy): {s}") from e

def _try_yaml_or_json_load(text: str):
    try:
        return yaml.safe_load(text)
    except Exception:
        return json.loads(text)

def load_config(path: str, registry) -> Dict[str, List[str]]:
    warnings = {"poi_types": [], "pois": [], "visitors": [], "visits": []}

    if not os.path.exists(path):
        raise ConfigError(f"File not found: {path}")
    text = open(path, "r", encoding="utf-8").read()

    data = _try_yaml_or_json_load(text)

    for t in data.get("poi_types", []):
        try:
            name = t.get("name")
            attrs = list(t.get("attributes", []))
            if not name or not isinstance(attrs, list):
                raise ConfigError("POI type must have 'name' and optional list 'attributes'.")
            registry.add_poi_type(name, attrs)
        except Exception as e:
            warnings["poi_types"].append(f"Type skipped: {e}")

    for p in data.get("pois", []):
        try:
            pid = int(p.get("id"))
            name = p.get("name")
            tname = p.get("type")
            x = int(p.get("x"))
            y = int(p.get("y"))
            attrs = dict(p.get("attributes", {}))
            if name is None or tname is None:
                raise ConfigError("POI requires 'id','name','type','x','y'.")
            registry.add_poi(pid, name, tname, x, y, attrs)
        except Exception as e:
            warnings["pois"].append(f"POI skipped: {e}")

    for v in data.get("visitors", []):
        try:
            vid = int(v.get("id"))
            name = v.get("name")
            nat = v.get("nationality")
            if name is None or nat is None:
                raise ConfigError("Visitor requires 'id','name','nationality'.")
            registry.add_visitor(vid, name, nat)
        except Exception as e:
            warnings["visitors"].append(f"Visitor skipped: {e}")

    for vv in data.get("visits", []):
        try:
            vid = int(vv.get("visitor_id"))
            pid = int(vv.get("poi_id"))
            date = _parse_date(vv.get("date"))
            rating = vv.get("rating", None)
            if rating is not None:
                rating = int(rating)
            registry.add_visit(vid, pid, date, rating)
        except Exception as e:
            warnings["visits"].append(f"Visit skipped: {e}")

    return warnings
