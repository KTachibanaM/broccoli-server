from typing import Tuple, Callable
from .getenv_or_raise import getenv_or_raise


def flask_auth_route(request, create_access_token_f: Callable[[str], str]) -> Tuple[int, str]:
    admin_username = getenv_or_raise("ADMIN_USERNAME")
    admin_password = getenv_or_raise("ADMIN_PASSWORD")

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return 400, "Missing username parameter"
    if not password:
        return 400, "Missing password parameter"
    if username != admin_username or password != admin_password:
        return 401, "Bad username or password"
    return 200, create_access_token_f(username)
