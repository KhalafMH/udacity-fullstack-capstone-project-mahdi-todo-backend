import json
from functools import wraps
from typing import Mapping
from urllib.request import urlopen

from flask import request
from jose import jwt, JWTError

AUTH0_DOMAIN = 'mahdi-todo.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'backend'


class AuthError(Exception):
    """
    AuthError Exception
    A standardized way to communicate auth failure modes
    """

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """
    Get the authorization token from the request `Authorization` header.

    :return: The authorization token in the request headers.
    :raises AuthError if the Authorization header is missing or malformed.
    """
    header = request.headers.get('Authorization') or request.headers.get('authorization')
    if header is None:
        raise AuthError('Authorization header missing', 401)
    split_header = header.split()
    if len(split_header) != 2 or split_header[0].lower() != 'bearer':
        raise AuthError('Malformed Authorization header', 401)
    return split_header[1]


def check_permissions(permission: str, payload: Mapping):
    """
    Check if the payload contains the required permission.

    :param permission: A permission string.
    :param payload: A decoded JWT payload.
    :return: True if the payload contains all the required permission.
    :raises AuthError if the payload does not include the permission.
    """
    payload_permissions = payload.get('permissions')
    if payload_permissions is None:
        raise AuthError('Permissions missing from payload', 401)
    if permission not in payload_permissions:
        raise AuthError(f'Payload does not include the {permission} permission', 401)

    return True


def verify_decode_jwt(token):
    """
    Verifies the validity of the provided token and returns the decoded payload.

    :param token: A JWT token.
    :return: The decoded JWT payload if the JWT is valid.
    :raises AuthError if the JWT is not valid.
    """
    keys = None
    with urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json') as response:
        keys = json.loads(response.read())['keys']
    for key in keys:
        try:
            claims = jwt.decode(token, algorithms=ALGORITHMS, audience=API_AUDIENCE, key=key)
            return claims
        except JWTError as e:
            pass
    raise AuthError('Invalid token', 401)


'''
TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''


def requires_auth_permission(permission=''):
    """
    A decorator that checks if the request is authenticated with the required permission.

    :param permission: A permission string.
    :return: A decorator that invokes the decorated function only if the request contains the required permission.
    :raises AuthError if no valid JWT is provided in the request headers.
    """

    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
