import io
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from territorial import ExternalCamera, Players, Territorial, allowed_image, allowed_player, embeddable, remote, road_url


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

    def test_official_euskadi_redirect_and_hispa_image_are_allowed(self):
        self.assertTrue(allowed_image('https://www.trafikoa.euskadi.eus/static/files/tr/camaras/819.jpg'))
        self.assertTrue(allowed_image('https://www.hispacams.com/get_imagen_ws.php?id=110&size=s'))
        self.assertFalse(allowed_image('https://www.hispacams.com/get_imagen_ws.php?url=http://localhost'))

    def test_only_main_camera_image_not_related_thumbnails(self):
        parser = Players()
        parser.feed('<img src="https://www.hispacams.com/get_imagen_ws.php?id=1&size=s"><img id="player" src="about:blank" data-lazy-src="https://www.hispacams.com/get_imagen_ws.php?id=2&size=l">')
        self.assertEqual(parser.images, ['https://www.hispacams.com/get_imagen_ws.php?id=2&size=l'])

    def test_embed_checks_frame_policy_and_player_markup(self):
        url = 'https://rtsp.me/embed/test/'
        self.assertTrue(embeddable(url, b'<video id="video"></video>', {}))
        self.assertFalse(embeddable(url, b'<h1>Not found</h1>', {}))
        self.assertFalse(embeddable(url, b'<video></video>', {'X-Frame-Options': 'SAMEORIGIN'}))
        self.assertFalse(embeddable(url, b'<video></video>', {'Content-Security-Policy': "frame-ancestors 'self'"}))
        self.assertFalse(embeddable('https://www.youtube.com/embed/12345678901', b'{"playabilityStatus":{"status":"UNPLAYABLE"}}', {}))

    def test_media_checks_keep_external_and_failed_cameras_out(self):
        from unittest.mock import Mock
        db = Mock()
        territorial = Territorial(db)
        with patch.object(territorial, '_webcam', return_value={'player_url': None}):
            with self.assertRaises(ExternalCamera):
                territorial.webcam('c1')
            self.assertEqual(db.camera_check.call_args.args[1], 'external')
        with patch.object(territorial, '_webcam', side_effect=RuntimeError('HTTP 404')):
            with self.assertRaises(RuntimeError):
                territorial.webcam('c2')
            self.assertEqual(db.camera_check.call_args.args[1], 'unavailable')
        with patch.object(territorial, '_webcam', return_value={'url': '/territorial/test.img'}):
            self.assertEqual(territorial.webcam('c3')['kind'], 'snapshot')
            self.assertEqual(db.camera_check.call_args.args[1], 'available')
        with patch.object(territorial, '_webcam', return_value={'player_url': 'https://rtsp.me/embed/test/'}):
            self.assertTrue(territorial.webcam('c4')['verification_pending'])
            self.assertEqual(db.camera_check.call_args.args[1], 'unavailable')
        with patch.object(territorial, '_webcam', return_value={'player_url': 'https://rtsp.me/embed/test/', 'browser_verified_until': 9999999999}):
            self.assertFalse(territorial.webcam('c4')['verification_pending'])
            self.assertEqual(db.camera_check.call_args.args[1], 'available')
        offline = Territorial(db, True)
        db.camera_check.reset_mock()
        with patch.object(offline, '_webcam', side_effect=RuntimeError('Sin copia')):
            with self.assertRaises(RuntimeError):
                offline.webcam('c3')
            db.camera_check.assert_not_called()

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

    def test_cached_unavailable_template_is_not_a_working_camera(self):
        import time
        from unittest.mock import Mock
        from territorial import UNAVAILABLE_IMAGES
        db = Mock()
        db.get_asset.return_value = {'path': 'test_territorial.py', 'data': {'sha256': next(iter(UNAVAILABLE_IMAGES)), 'fetched_epoch': time.time()}}
        with patch('territorial.remote') as fetch:
            with self.assertRaisesRegex(RuntimeError, 'plantilla'):
                Territorial(db).cached_image('camera:test', 'https://etraffic.dgt.es/camarasEtraffic/1.jpg', allowed_image, 180, 'webcam')
            fetch.assert_not_called()

    def test_road_bounds_and_fixed_layer(self):
        self.assertIn('TN.RoadTransportNetwork.RoadLink', road_url(6, 31, 24))
        self.assertIn('EPSG%3A3857', road_url(6, 31, 24))
        for args in [(0, 0, 0), (17, 0, 0), (5, -1, 2), (6, 64, 20), (6, 0, 0)]:
            with self.assertRaises(ValueError):
                road_url(*args)


if __name__ == '__main__':
    unittest.main()
