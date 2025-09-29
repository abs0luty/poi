import unittest
from poi_system import POIRegistry

class TestTypeAndAttributes(unittest.TestCase):
    def test_type_deletion_constraint(self):
        r = POIRegistry()
        r.add_poi_type("park", ["size"])
        r.add_poi(1, "P", "park", 1, 1, {"size":"small"})
        with self.assertRaises(Exception):
            r.delete_poi_type("park")
        r.delete_poi(1)
        r.delete_poi_type("park")  # now OK

    def test_attribute_rename_migration(self):
        r = POIRegistry()
        r.add_poi_type("museum", ["theme"])
        r.add_poi(1, "M", "museum", 1, 2, {"theme":"art"})
        r.rename_attribute("museum", "theme", "topic")
        self.assertIn("topic", r.pois[1].attributes)
        self.assertNotIn("theme", r.pois[1].attributes)

if __name__ == "__main__":
    unittest.main()
