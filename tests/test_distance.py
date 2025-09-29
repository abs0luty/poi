import unittest
from poi_system import POIRegistry

class TestDistanceAndBoundary(unittest.TestCase):
    def test_epsilon_boundary(self):
        r = POIRegistry()
        r.add_poi_type("t", [])
        r.add_poi(1, "A", "t", 0, 0, {})
        r.add_poi(2, "B", "t", 3, 4, {})  # distance 5 exactly
        within = r.pois_within_radius((0,0), 5.0)
        self.assertTrue(any(p[0]==2 for p in within), "B should be within r=5")
        exact = r.at_exact_radius((0,0), 5.0)
        self.assertTrue(any(p[0]==2 for p in exact), "B should be exactly at r=5")

    def test_k_closest_tie_break(self):
        r = POIRegistry()
        r.add_poi_type("t", [])
        r.add_poi(10, "A", "t", 1, 0, {})
        r.add_poi(2, "B", "t", 0, 1, {})
        k2 = r.k_closest((0,0), 2)
        # Distances are equal (~1), tie broken by id ascending then name: id=2 first, then id=10
        self.assertEqual([k2[0][0], k2[1][0]], [2,10])

if __name__ == "__main__":
    unittest.main()
