import unittest

from local_routes import RoadGraph, route_bounds


def way(identifier, nodes, coordinates, **tags):
    return {'type': 'way', 'id': identifier, 'nodes': nodes,
            'geometry': [{'lon': p[0], 'lat': p[1]} for p in coordinates], 'tags': {'highway': 'residential', **tags}}


class LocalRouteTests(unittest.TestCase):
    def test_closure_changes_geometry_and_congestion_changes_time(self):
        graph = RoadGraph({'elements': [
            way(1, [1, 2, 3], [(2.1, 41.4), (2.101, 41.4), (2.102, 41.4)]),
            way(2, [1, 4, 3], [(2.1, 41.4), (2.101, 41.401), (2.102, 41.4)]),
        ]})
        direct = graph.route([2.1, 41.4], [2.102, 41.4])
        detour = graph.route([2.1, 41.4], [2.102, 41.4], blocked={'1:2'})
        self.assertNotEqual(direct['coordinates'], detour['coordinates'])
        self.assertNotIn('1:2', detour['edge_ids'])
        delayed = graph.route([2.1, 41.4], [2.102, 41.4], congestion={'1:2': 5})
        self.assertGreater(delayed['duration_seconds'], direct['duration_seconds'])
        with self.assertRaises(ValueError):
            graph.route([2.1, 41.4], [2.102, 41.4], blocked={'1:2', '1:4'})

    def test_connected_route_and_oneway(self):
        graph = RoadGraph({'elements': [way(1, [1, 2, 3], [(1, 41), (1.001, 41), (1.002, 41)], oneway='yes')]})
        route = graph.route([1, 41], [1.002, 41])
        self.assertEqual(route['coordinates'], [[1, 41], [1.001, 41], [1.002, 41]])
        self.assertGreater(route['distance_km'], .1)
        with self.assertRaises(ValueError):
            graph.route([1.002, 41], [1, 41])

    def test_disconnected_fragment_anchors_to_connected_network_without_fake_geometry(self):
        elements = [way(1, [1, 2, 5], [(1, 41), (1.001, 41), (1.0015, 41)]), way(2, [3, 4], [(1.002, 41), (1.003, 41)])]
        graph = RoadGraph({'elements': elements})
        self.assertEqual(graph.connected, {1, 2, 5})
        route = graph.route([1, 41], [1.003, 41])
        self.assertEqual(route['coordinates'][-1], [1.0015, 41])
        self.assertGreater(route['end_gap_m'], 100)
        self.assertFalse(route.get('approximate'))
        elements.append(way(3, [5, 3], [(1.0015, 41), (1.002, 41)], access='private'))
        private = RoadGraph({'elements': elements}).route([1, 41], [1.003, 41])
        self.assertNotIn([1.002, 41], private['coordinates'])

    def test_isolated_stub_next_to_target_does_not_exhaust_search(self):
        # Caso Tibidabo: el nodo más próximo al destino pertenece a un tramo suelto de pocos metros.
        elements = [way(1, [1, 2, 3], [(2.1, 41.4), (2.101, 41.4), (2.102, 41.4)]),
                    way(2, [8, 9], [(2.1021, 41.4003), (2.1022, 41.4003)])]
        graph = RoadGraph({'elements': elements})
        route = graph.route([2.1, 41.4], [2.1021, 41.4003])
        self.assertEqual(route['coordinates'][-1], [2.102, 41.4])
        self.assertLess(route['end_gap_m'], 60)

    def test_relaxed_route_ignores_oneway_but_never_closures(self):
        graph = RoadGraph({'elements': [way(1, [1, 2, 3], [(1, 41), (1.001, 41), (1.002, 41)], oneway='yes')]})
        with self.assertRaises(ValueError):
            graph.route([1.002, 41], [1, 41])
        relaxed = graph.route([1.002, 41], [1, 41], relaxed=True)
        self.assertTrue(relaxed['approximate'])
        self.assertEqual(relaxed['coordinates'], [[1.002, 41], [1.001, 41], [1, 41]])
        with self.assertRaises(ValueError):
            graph.route([1.002, 41], [1, 41], blocked={'1:2'}, relaxed=True)

    def test_reverse_oneway_and_roundabout(self):
        graph = RoadGraph({'elements': [way(1, [1, 2], [(1, 41), (1.001, 41)], oneway='-1')]})
        self.assertEqual(graph.route([1.001, 41], [1, 41])['coordinates'][-1], [1, 41])
        with self.assertRaises(ValueError):
            graph.route([1, 41], [1.001, 41])
        graph = RoadGraph({'elements': [way(1, [1, 2], [(1, 41), (1.001, 41)], junction='roundabout')]})
        with self.assertRaises(ValueError):
            graph.route([1.001, 41], [1, 41])

    def test_routing_api_fallback_returns_real_geometry_without_overpass(self):
        import io
        import json
        from unittest.mock import Mock, patch
        from local_routes import LocalRouter
        body = {'code': 'Ok', 'routes': [{'duration': 60, 'geometry': {'type': 'LineString', 'coordinates': [[1, 41], [1.001, 41], [1.002, 41]]}}]}
        db = Mock()
        db.get_asset.return_value = None
        router = LocalRouter(db)
        with patch('local_routes.urlopen', side_effect=[OSError('timeout'), io.BytesIO(json.dumps(body).encode())]) as network, patch('local_routes.time.sleep'), patch.object(LocalRouter, 'route_unavailable', {}), patch.object(router, 'download') as download:
            route = router.route([1, 41], [1.002, 41])
        self.assertEqual(network.call_count, 2)
        self.assertEqual(route['mode'], 'road_api')
        self.assertEqual(len(route['coordinates']), 3)
        self.assertGreater(route['distance_km'], .1)
        download.assert_not_called()

    def test_routing_api_rejects_invented_or_distant_endpoints(self):
        import io
        import json
        from unittest.mock import Mock, patch
        from local_routes import LocalRouter
        body = {'code': 'Ok', 'routes': [{'duration': 60, 'geometry': {'type': 'LineString', 'coordinates': [[2, 42], [2.01, 42]]}}]}
        with patch('local_routes.urlopen', side_effect=lambda *a, **k: io.BytesIO(json.dumps(body).encode())), patch('local_routes.time.sleep'), patch.object(LocalRouter, 'route_unavailable', {}):
            with self.assertRaises(RuntimeError):
                LocalRouter(Mock()).remote_route([1, 41], [1.002, 41])

    def test_barcelona_query_is_local_not_the_whole_metropolitan_area(self):
        south, west, north, east = route_bounds([2.1986627, 41.4051832], [2.1744283, 41.4035046])
        self.assertLess((east - west) * (north - south), .01)

    def test_download_uses_alternate_provider_after_timeout(self):
        import io
        import json
        from unittest.mock import Mock, patch
        from urllib.error import HTTPError
        from local_routes import LocalRouter
        data = {'elements': [way(1, [1, 2], [(1, 41), (1.001, 41)])]}
        with patch('local_routes.urlopen', side_effect=[HTTPError('fixture', 504, 'Timeout', {}, None), io.BytesIO(json.dumps(data).encode())]) as fetch, patch('local_routes.time.sleep'):
            result = LocalRouter(Mock()).download((40.98, .98, 41.02, 1.02))
        self.assertEqual(len(result['elements']), 1)
        self.assertEqual(fetch.call_count, 2)
        self.assertNotEqual(fetch.call_args_list[0].args[0].full_url, fetch.call_args_list[1].args[0].full_url)

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
