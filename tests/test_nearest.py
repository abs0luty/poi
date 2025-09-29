import unittest
from poi_system import POIRegistry

class TestNearestQueries(unittest.TestCase):
    def test_closest_pair(self):
        r = POIRegistry()
        r.add_poi_type("t", [])
        r.add_poi(1, "A", "t", 0, 0, {})
        r.add_poi(2, "B", "t", 3, 0, {})
        r.add_poi(3, "C", "t", 4, 0, {})
        pair = r.closest_pair()
        # The closest pair should be (2,3) with distance 1
        self.assertIn(pair[0][0], (2,3))
        self.assertIn(pair[1][0], (2,3))

    def test_within_and_k_closest(self):
        r = POIRegistry()
        r.add_poi_type("t", [])
        r.add_poi(1, "A", "t", 0, 0, {})
        r.add_poi(2, "B", "t", 1, 0, {})
        r.add_poi(3, "C", "t", 0, 2, {})
        within = r.pois_within_radius((0,0), 1.0)
        ids = [i[0] for i in within]
        self.assertEqual(ids, [1,2])  # A (0), B (1), C (2)
        k2 = r.k_closest((0,0), 2)
        self.assertEqual([k2[0][0],k2[1][0]],[1,2])

if __name__ == "__main__":
    unittest.main()
