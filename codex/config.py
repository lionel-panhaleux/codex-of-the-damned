import os


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    # Translation
    SUPPORTED_LANGUAGES = {"en": "English", "fr": "Francais"}
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "UTC"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False


config = {
    "dev": "codex.config.DevelopmentConfig",
    "prod": "codex.config.ProductionConfig",
    "default": "codex.config.DevelopmentConfig",
}


def configure_app(app):
    config_name = os.getenv("FLASK_CONFIGURATION", "default")
    app.config.from_object(config[config_name])
    app.config.from_pyfile("config.cfg", silent=True)
