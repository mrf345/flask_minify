from sys import path as sys_path
from os import path
from importlib import import_module

from flask_minify.utils import (is_empty, is_html)


sys_path.append(path.dirname(path.dirname(__file__)))
minify = import_module('flask_minify').minify
unittest = import_module('unittest')

# workaround for py2 vs py3 mock import
mock = getattr(unittest, 'mock', None) or import_module('mock')


class TestUtils:
    def test_is_empty(self):
        ''' Test is_empty check is correct '''

        assert is_empty('Not empty at all') is False
        assert is_empty('\n\t  \t\n\n' * 10) is True

    def test_is_html(self):
        ''' Test is_html check is correct '''
        assert is_html(mock.Mock('application/json')) is False
        assert is_html(mock.Mock(content_type='text/html')) is True


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
        self.patch = mock.patch.multiple('flask_minify.main',
                                         request=self.mock_request)

        self.patch.start()

    def teardown(self):
        self.patch.stop()

    @property
    def minify_defaults(self):
        return minify(self.mock_app, self.js, self.cssless, self.fail_safe,
                      self.bypass, self.bypass_caching, self.caching_limit)

    def test_request_falsy_endpoint(self):
        ''' test edge-case of request's endpoint being falsy '''
        endpoint = '/testing'
        self.mock_request.endpoint = None
        self.bypass.append(endpoint)

        assert self.minify_defaults.get_endpoint_matches([endpoint]) == []
