import os


class BaseConfig(object):
    DEBUG = os.environ.get("DEBUG", False)
    TESTING = DEBUG
    # Translation
    SUPPORTED_LANGUAGES = {"en": "English", "fr": "Francais"}
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "UTC"


def configure_app(app):
    app.config.from_object(BaseConfig)
