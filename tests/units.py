from unittest import mock

import pytest

from flask_minify import minify, parsers
from flask_minify.cache import MemoryCache
from flask_minify.exceptions import FlaskMinifyException
from flask_minify.utils import does_content_type_match, is_empty

from .constants import (
    COMPILED_LESS_RAW,
    CSS_EDGE_CASES,
    LESS_RAW,
    MINIFIED_CSS_EDGE_CASES,
)


class TestUtils:
    def test_is_empty(self):
        """Test is_empty check is correct"""
        assert is_empty("Not empty at all") is False
        assert is_empty("\n\t  \t\n\n" * 10) is True

    def test_is_html(self):
        """Test is_html check is correct"""
        assert does_content_type_match(mock.Mock("application/json"))[0] is False
        assert does_content_type_match(mock.Mock(content_type="text/html"))[0] is True

    def test_is_js(self):
        """Test is_js check is correct"""
        assert does_content_type_match(mock.Mock(content_type="text/html"))[2] is False
        assert (
            does_content_type_match(mock.Mock(content_type="text/javascript"))[2]
            is True
        )
        assert (
            does_content_type_match(mock.Mock(content_type="application/javascript"))[2]
            is True
        )

    def test_is_cssless(self):
        """Test is_cssless check is correct"""
        assert (
            does_content_type_match(mock.Mock(content_type="text/javascript"))[1]
            is False
        )
        assert does_content_type_match(mock.Mock(content_type="text/css"))[1] is True
        assert does_content_type_match(mock.Mock(content_type="text/less"))[1] is True


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
            [endpoint],
        )

        assert (list(matches), exists) == ([], False)

    def test_access_app_after_lazy_initialization(self):
        """"""
        self.mock_app = None
        ext = self.minify_defaults
        mock_app = mock.MagicMock()
        ext.init_app(mock_app)

        assert ext.app == mock_app


class TestParsers:
    def test_css_edge_cases_with_rcssmin(self):
        parser = parsers.Parser({"style": parsers.Rcssmin})
        minified = parser.minify(CSS_EDGE_CASES, "style")

        assert minified == MINIFIED_CSS_EDGE_CASES

    def test_overriding_parser_options(self):
        new_options = {"minify": False}

        class CustomParser(parsers.Lesscpy):
            runtime_options = new_options

        parser = parsers.Parser({"style": CustomParser})
        minified = parser.minify(LESS_RAW, "style")

        assert minified == COMPILED_LESS_RAW

    def test_parser_raising_exception_with_failsafe_disabled(self):
        class CustomParser(parsers.Lesscpy):
            def executer(self, content, **options):
                raise Exception("something went wrong")

        parser = parsers.Parser({"style": CustomParser})

        with pytest.raises(FlaskMinifyException):
            parser.minify(LESS_RAW, "style")


class TestMemoryCache:
    def setup(self):
        self.store_key_getter = lambda: "testing"
        self.limit = 2
        self.content = "test something to cache with"
        self.to_cache = "testingsomethintocachehopefully"

    def get_cache(self):
        return MemoryCache(
            self.store_key_getter,
            self.limit,
        )

    def test_caching_is_fixed_size(self):
        cache = self.get_cache()
        getter = lambda: self.to_cache
        minified = {cache.get_or_set(self.content, getter) for _ in range(100)}

        assert minified == {self.to_cache}
        assert len(cache.store) == 1

    def test_caching_limit_exceeded(self):
        self.limit = 99
        cache = self.get_cache()
        scope = 100
        minified = {
            cache.get_or_set(
                f"{self.content}{i}",
                lambda: f"{self.to_cache}{i}",
            )
            for i in range(scope)
        }

        assert len(minified) == scope
        assert len(cache.store) == self.limit

    def test_disable_caching(self):
        self.limit = 0
        cache = self.get_cache()
        scope = 100
        minified = {
            cache.get_or_set(
                f"{self.content}{i}",
                lambda: f"{self.to_cache}{i}",
            )
            for i in range(scope)
        }

        assert len(minified) == scope
        assert cache.store == {}
