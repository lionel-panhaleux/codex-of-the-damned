import os
from typing import ClassVar


class BaseConfig:
    DEBUG = os.environ.get("DEBUG")
    TESTING = DEBUG
    # Translation
    SUPPORTED_LANGUAGES: ClassVar[dict[str, str]] = {
        "en": "English",
        "fr": "Francais",
        "es": "Espanol",
        "pt": "Portugues",
    }
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "UTC"


def configure_app(app):
    app.config.from_object(BaseConfig)
