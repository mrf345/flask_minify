from os import path
from sys import path as sys_path
from unittest import mock

from flask_minify import minify, parsers
from flask_minify.utils import is_cssless, is_empty, is_html, is_js

from .constants import CSS_EDGE_CASES, MINIFIED_CSS_EDGE_CASES


class TestUtils:
    def test_is_empty(self):
        """Test is_empty check is correct"""
        assert is_empty("Not empty at all") is False
        assert is_empty("\n\t  \t\n\n" * 10) is True

    def test_is_html(self):
        """Test is_html check is correct"""
        assert is_html(mock.Mock("application/json")) is False
        assert is_html(mock.Mock(content_type="text/html")) is True

    def test_is_js(self):
        """Test is_js check is correct"""
        assert is_js(mock.Mock(content_type="text/html")) is False
        assert is_js(mock.Mock(content_type="text/javascript")) is True
        assert is_js(mock.Mock(content_type="application/javascript")) is True

    def test_is_cssless(self):
        """Test is_cssless check is correct"""
        assert is_cssless(mock.Mock(content_type="text/javascript")) is False
        assert is_cssless(mock.Mock(content_type="text/css")) is True
        assert is_cssless(mock.Mock(content_type="text/less")) is True


class TestMinifyRequest:
    def setup(self):
        self.mock_request = mock.Mock()
        self.mock_app = mock.Mock()
        self.mock_app.app_context.return_value = mock.MagicMock()
        self.js = False
        self.cssless = False
        self.fail_safe = False
        self.bypass = []
        self.bypass_caching = []
        self.caching_limit = 1
        self.patch = mock.patch.multiple("flask_minify.main", request=self.mock_request)

        self.patch.start()

    def teardown(self):
        self.patch.stop()

    @property
    def minify_defaults(self):
        return minify(
            self.mock_app,
            self.js,
            self.cssless,
            self.fail_safe,
            self.bypass,
            self.bypass_caching,
            self.caching_limit,
        )

    def test_request_falsy_endpoint(self):
        """test edge-case of request's endpoint being falsy"""
        endpoint = "/testing"
        self.mock_request.endpoint = None
        self.bypass.append(endpoint)
        matches, exists = self.minify_defaults.get_endpoint_matches(
            self.minify_defaults.endpoint,
            [endpoint],
        )

        assert (list(matches), exists) == ([], False)


class TestParsers:
    def test_css_edge_cases_with_rcssmin(self):
        parser = parsers.Parser({"style": parsers.Rcssmin})
        minified = parser.minify(CSS_EDGE_CASES, "style")

        assert minified == MINIFIED_CSS_EDGE_CASES
