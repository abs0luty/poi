from typing import Tuple

from .storage import POIRegistry, POIError
from .config_loader import load_config

MENU_TEXT = """
POI Management System (CLI)
---------------------------
1) Load configuration (YAML or JSON)
2) Add POI type
3) Delete POI type
4) Add attribute to type
5) Delete attribute from type
6) Rename attribute (extension)
7) Rename POI type (extension)
8) Add POI
9) Delete POI
10) Add visitor
11) Add visit
12) List POIs by type
13) Closest pair of POIs
14) Count POIs per type
15) POIs within radius
16) k closest POIs
17) Boundary: exactly at radius
18) Visitor -> visited POIs
19) Number of visitors per POI
20) Number of POIs per visitor
21) Top-k visitors by distinct POIs
22) Top-k POIs by distinct visitors
23) Coverage fairness (m,t)
0) Exit
"""

def run_cli():
    r = POIRegistry()
    print(MENU_TEXT)
    while True:
        try:
            choice = ask_str("Select option: ")
            if choice == "1":
                path = ask_str("Path to config file: ")
                warnings = load_config(path, r)
                print("Loaded. Warnings:")
                for k, arr in warnings.items():
                    for w in arr:
                        print(f"[{k}] {w}")
            elif choice == "2":
                t = ask_str("Type name: ")
                attrs = ask_str("Attributes (comma-separated, optional): ")
                attr_list = [a.strip() for a in attrs.split(",") if a.strip()] if attrs else []
                r.add_poi_type(t, attr_list)
                print("Type added.")
            elif choice == "3":
                t = ask_str("Type name to delete: ")
                r.delete_poi_type(t)
                print("Type deleted.")
            elif choice == "4":
                t = ask_str("Type name: ")
                a = ask_str("Attribute to add: ")
                r.add_attribute(t, a)
                print("Attribute added.")
            elif choice == "5":
                t = ask_str("Type name: ")
                a = ask_str("Attribute to delete: ")
                r.delete_attribute(t, a)
                print("Attribute deleted.")
            elif choice == "6":
                t = ask_str("Type name: ")
                old = ask_str("Old attribute name: ")
                new = ask_str("New attribute name: ")
                r.rename_attribute(t, old, new)
                print("Attribute renamed.")
            elif choice == "7":
                old = ask_str("Old type name: ")
                new = ask_str("New type name: ")
                r.rename_type(old, new)
                print("Type renamed.")
            elif choice == "8":
                pid = ask_int("POI id (int): ")
                name = ask_str("POI name: ")
                t = ask_str("Type name: ")
                print("Coordinates (integers 0..999)")
                x,y = ask_xy()
                attrs = ask_str("Attributes as key=value,comma-separated (optional): ")
                attr_dict = {}
                if attrs.strip():
                    for pair in attrs.split(","):
                        if "=" in pair:
                            k,v = pair.split("=",1)
                            attr_dict[k.strip()] = v.strip()
                r.add_poi(pid, name, t, x, y, attr_dict)
                print("POI added.")
            elif choice == "9":
                pid = ask_int("POI id to delete: ")
                r.delete_poi(pid)
                print("POI deleted.")
            elif choice == "10":
                vid = ask_int("Visitor id (int): ")
                name = ask_str("Visitor name: ")
                nat = ask_str("Nationality: ")
                r.add_visitor(vid, name, nat)
                print("Visitor added.")
            elif choice == "11":
                vid = ask_int("Visitor id: ")
                pid = ask_int("POI id: ")
                date = ask_str("Date (dd/mm/yyyy): ")
                rating_s = ask_str("Rating 1..10 (optional): ")
                rating = int(rating_s) if rating_s.strip() else None
                r.add_visit(vid, pid, date, rating)
                print("Visit added.")
            elif choice == "12":
                t = ask_str("Type: ")
                for row in r.list_pois_by_type(t):
                    print(row)
            elif choice == "13":
                res = r.closest_pair()
                print(res if res else "Need at least two POIs.")
            elif choice == "14":
                for t,c in r.count_pois_per_type():
                    print(f"{t}: {c}")
            elif choice == "15":
                print("Center c0:")
                x,y = ask_xy()
                r0 = float(ask_str("radius r: "))
                for row in r.pois_within_radius((x,y), r0):
                    print(row)
            elif choice == "16":
                print("Center c0:")
                x,y = ask_xy()
                k = ask_int("k: ")
                for row in r.k_closest((x,y), k):
                    print(row)
            elif choice == "17":
                print("Center c0:")
                x,y = ask_xy()
                r0 = float(ask_str("radius r: "))
                for row in r.at_exact_radius((x,y), r0):
                    print(row)
            elif choice == "18":
                vid = ask_int("Visitor id: ")
                for row in r.visits_for_visitor(vid):
                    print(row)
            elif choice == "19":
                for row in r.number_of_visitors_per_poi():
                    print(row)
            elif choice == "20":
                for row in r.number_of_pois_per_visitor():
                    print(row)
            elif choice == "21":
                k = ask_int("k: ")
                for row in r.top_k_visitors_by_poi_count(k):
                    print(row)
            elif choice == "22":
                k = ask_int("k: ")
                for row in r.top_k_pois_by_visitor_count(k):
                    print(row)
            elif choice == "23":
                m = ask_int("m: ")
                t = ask_int("t: ")
                for row in r.coverage_fairness(m, t):
                    print(row)
            elif choice == "0":
                print("Bye.")
                return
            else:
                print("Unknown option.")
        except POIError as e:
            print(f"[Error] {e}")
        except Exception as e:
            print(f"[Unexpected] {e}")

def ask_int(prompt: str) -> int:
    return int(input(prompt).strip())

def ask_str(prompt: str) -> str:
    return input(prompt).strip()

def ask_xy() -> Tuple[int,int]:
    x = ask_int("x = ")
    y = ask_int("y = ")
    return (x,y)


if __name__ == "__main__":
    run_cli()
