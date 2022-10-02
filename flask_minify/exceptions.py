class FlaskMinifyException(Exception):
    """FlaskMinify base exception"""

    pass


class MissingApp(FlaskMinifyException):
    """Raised when the flask app is accessed before it's set"""

    pass
