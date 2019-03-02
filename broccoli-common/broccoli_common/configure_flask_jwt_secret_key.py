from .getenv_or_raise import getenv_or_raise


def configure_flask_jwt_secret_key(flask_app):
    flask_app.config["JWT_SECRET_KEY"] = getenv_or_raise("JWT_SECRET_KEY")

