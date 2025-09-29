import unittest, json, os
from poi_system import POIRegistry, load_config

class TestConfigLoader(unittest.TestCase):
    def test_load_config_and_validation(self):
        r = POIRegistry()
        data = {
            "poi_types":[{"name":"park","attributes":["a1","a2"]}],
            "pois":[
                {"id": 1, "name":"P1","type":"park","x": 10, "y": 10, "attributes":{"a1":1}},
                {"id": 1, "name":"P2","type":"park","x": 10, "y": 10, "attributes":{"a1":1}}  # duplicate id -> skipped
            ],
            "visitors":[{"id":1,"name":"V1","nationality":"AE"}],
            "visits":[{"visitor_id":1,"poi_id":1,"date":"01/01/2024","rating":5}]
        }
        path = "./tests/tmp_config.json"
        with open(path, "w") as f:
            json.dump(data, f)
        warnings = load_config(path, r)
        self.assertEqual(len(warnings["pois"]), 1)
        self.assertIn(1, r.pois)
        self.assertIn(1, r.visitors)
        v = r.visits_for_visitor(1)
        self.assertEqual(len(v), 1)

if __name__ == "__main__":
    unittest.main()
