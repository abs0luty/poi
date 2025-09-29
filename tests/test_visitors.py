import unittest
from poi_system import POIRegistry

class TestVisitorStats(unittest.TestCase):
    def setUp(self):
        self.r = POIRegistry()
        self.r.add_poi_type("park", [])
        self.r.add_poi_type("museum", [])
        self.r.add_poi(1, "P1", "park", 0, 0, {})
        self.r.add_poi(2, "M1", "museum", 5, 0, {})
        self.r.add_visitor(1, "A", "AE")
        self.r.add_visitor(2, "B", "AE")
        self.r.add_visit(1, 1, "01/01/2024", 7)
        self.r.add_visit(1, 2, "02/01/2024", 8)
        self.r.add_visit(2, 1, "02/01/2024", 8)

    def test_number_of_visitors_per_poi(self):
        counts = dict(self.r.number_of_visitors_per_poi())  
        self.assertEqual(counts[1], 2)
        self.assertEqual(counts[2], 1)

    def test_number_of_pois_per_visitor(self):
        counts = dict(self.r.number_of_pois_per_visitor())  
        self.assertEqual(counts[1], 2)
        self.assertEqual(counts[2], 1)

    def test_top_k(self):
        top_visitors = self.r.top_k_visitors_by_poi_count(2)
        self.assertEqual(top_visitors[0][0], 1) 
        top_pois = self.r.top_k_pois_by_visitor_count(2)
        self.assertEqual(top_pois[0][0], 1) 

if __name__ == "__main__":
    unittest.main()
