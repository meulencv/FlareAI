import unittest

from local_routes import RoadGraph, route_bounds


def way(identifier, nodes, coordinates, **tags):
    return {'type': 'way', 'id': identifier, 'nodes': nodes,
            'geometry': [{'lon': p[0], 'lat': p[1]} for p in coordinates], 'tags': {'highway': 'residential', **tags}}


class LocalRouteTests(unittest.TestCase):
    def test_connected_route_and_oneway(self):
        graph = RoadGraph({'elements': [way(1, [1, 2, 3], [(1, 41), (1.001, 41), (1.002, 41)], oneway='yes')]})
        route = graph.route([1, 41], [1.002, 41])
        self.assertEqual(route['coordinates'], [[1, 41], [1.001, 41], [1.002, 41]])
        self.assertGreater(route['distance_km'], .1)
        with self.assertRaises(ValueError):
            graph.route([1.002, 41], [1, 41])

    def test_disconnected_and_private_are_not_fake_routes(self):
        elements = [way(1, [1, 2], [(1, 41), (1.001, 41)]), way(2, [3, 4], [(1.002, 41), (1.003, 41)])]
        graph = RoadGraph({'elements': elements})
        with self.assertRaises(ValueError):
            graph.route([1, 41], [1.003, 41])
        elements.append(way(3, [2, 3], [(1.001, 41), (1.002, 41)], access='private'))
        with self.assertRaises(ValueError):
            RoadGraph({'elements': elements}).route([1, 41], [1.003, 41])

    def test_reverse_oneway_and_roundabout(self):
        graph = RoadGraph({'elements': [way(1, [1, 2], [(1, 41), (1.001, 41)], oneway='-1')]})
        self.assertEqual(graph.route([1.001, 41], [1, 41])['coordinates'][-1], [1, 41])
        with self.assertRaises(ValueError):
            graph.route([1, 41], [1.001, 41])
        graph = RoadGraph({'elements': [way(1, [1, 2], [(1, 41), (1.001, 41)], junction='roundabout')]})
        with self.assertRaises(ValueError):
            graph.route([1.001, 41], [1, 41])

    def test_too_far_from_road_and_bounded_download(self):
        graph = RoadGraph({'elements': [way(1, [1, 2], [(1, 41), (1.001, 41)])]})
        with self.assertRaises(ValueError):
            graph.route([1, 42], [1, 41])
        south, west, north, east = route_bounds([1, 41], [1.02, 41.01])
        self.assertLess(south, 41)
        self.assertGreater(north, 41.01)
        self.assertLess(west, 1)
        self.assertGreater(east, 1.02)
        with self.assertRaises(ValueError):
            route_bounds([-3, 40], [1, 41])


if __name__ == '__main__':
    unittest.main()
