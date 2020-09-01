import json
import os
from functools import wraps
from typing import Mapping
from urllib.request import urlopen

from flask import request
from jose import jwt, JWTError

AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
ALGORITHMS = [os.environ['AUTH0_SIGNING_ALGORITHM'] or 'RS256']
API_AUDIENCE = os.environ['AUTH0_API_AUDIENCE']


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


def check_user_id(user_id: str, payload: Mapping):
    """
    Check if the payload contains the required user_id.

    :param user_id: A user id string.
    :param payload: A decoded JWT payload.
    :return: True if the payload has the same subject as the user_id.
    :raises AuthError if the payload does not include a matching subject.
    """
    payload_subject = payload.get('sub')
    if payload_subject is None:
        raise AuthError('Subject missing from payload', 401)
    if user_id != payload_subject:
        raise AuthError(f'Request is not autheticated by user with id "{user_id}"', 401)

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


def requires_auth_user():
    """
    A decorator that checks if the request is authenticated with the required user id.
    NOTE: Requires that the user id is passed to the wrapped function in a parameter named user_id.

    :return: A decorator that invokes the decorated function only if the request contains the required user id.
    :raises AuthError if no valid JWT is provided in the request headers or if the user_id is not matching.
    """

    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = kwargs['user_id']
            payload = args[0]

            check_user_id(user_id, payload)

            return f(*args, **kwargs)

        return wrapper

    return requires_auth_decorator
