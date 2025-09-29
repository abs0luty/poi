from poi_system import POIRegistry, load_config
from pprint import pprint

r = POIRegistry()
warnings = load_config("./sample_config.json", r)
print("Warnings:", warnings)

print("\nPOIs per type:")
print(r.count_pois_per_type())

print("\nWithin radius r=12 from c0=(10,10):")
pprint(r.pois_within_radius((10,10), 12.0))

print("\nTop-2 visitors by POI count:")
print(r.top_k_visitors_by_poi_count(2))

print("\nCoverage fairness m=2, t=2:")
print(r.coverage_fairness(2,2))
