import io
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from territorial import Players, allowed_image, allowed_player, remote, road_url


class TerritorialTests(unittest.TestCase):
    def test_image_allowlist(self):
        for url in ['https://etraffic.dgt.es/camarasEtraffic/12.jpg', 'http://mct.gencat.cat/mct2bo/RenderService?cameraID=1']:
            self.assertTrue(allowed_image(url))
        for url in ['http://127.0.0.1/x.jpg', 'https://etraffic.dgt.es.evil.org/camarasEtraffic/1.jpg',
                    'https://user:pass@etraffic.dgt.es/camarasEtraffic/1.jpg', 'file:///etc/passwd',
                    'https://etraffic.dgt.es:8443/camarasEtraffic/1.jpg', 'http://etraffic.dgt.es/camarasEtraffic/1.jpg']:
            self.assertFalse(allowed_image(url))

    def test_public_iframe_only(self):
        parser = Players()
        parser.feed('<iframe src="http://127.0.0.1"></iframe><iframe data-lazy-src="https://rtsp.me/embed/abc12/"></iframe>')
        self.assertEqual(parser.urls, ['https://rtsp.me/embed/abc12/'])
        self.assertFalse(allowed_player('https://rtsp.me/stream/secret'))
        self.assertFalse(allowed_player('https://rtsp.me.evil.org/embed/a'))

    def test_redirect_revalidated_before_request(self):
        error = HTTPError('https://etraffic.dgt.es/camarasEtraffic/1.jpg', 302, 'redirect', {'Location': 'http://127.0.0.1/private'}, io.BytesIO())
        with patch('territorial.build_opener') as make:
            make.return_value.open.side_effect = error
            with self.assertRaises(RuntimeError):
                remote('https://etraffic.dgt.es/camarasEtraffic/1.jpg', allowed_image)
            self.assertEqual(make.return_value.open.call_count, 1)

    def test_response_limit(self):
        class Response(io.BytesIO):
            headers = {'Content-Type': 'image/jpeg'}
        with patch('territorial.build_opener') as make:
            make.return_value.open.return_value = Response(b'123456')
            with self.assertRaises(RuntimeError):
                remote('https://etraffic.dgt.es/camarasEtraffic/1.jpg', allowed_image, limit=5)

    def test_road_bounds_and_fixed_layer(self):
        self.assertIn('TN.RoadTransportNetwork.RoadLink', road_url(6, 31, 24))
        self.assertIn('EPSG%3A3857', road_url(6, 31, 24))
        for args in [(0, 0, 0), (17, 0, 0), (5, -1, 2), (6, 64, 20), (6, 0, 0)]:
            with self.assertRaises(ValueError):
                road_url(*args)


if __name__ == '__main__':
    unittest.main()
