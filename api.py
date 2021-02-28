"""Helper class to handle Up api requests."""

from contextlib import contextmanager
from os import environ

import jsonapi_requests
from requests.auth import AuthBase


class UpAuth(AuthBase):
    """A requests auth class which sets the authorization header."""

    def __init__(self):
        """Initialise the instances."""
        self.__user_environment_variable = None

    @property
    def bearer_token(self):
        """Return the bearer token for the current user."""
        return environ[self.current_user]

    @property
    def current_user(self):
        """Return the current_user raising ValueError if not set."""
        if self.__user_environment_variable is None:
            raise ValueError("There is no current user")
        return self.__user_environment_variable

    def __call__(self, request):
        """Add the authorization header."""
        request.headers["Authorization"] = f"Bearer {self.bearer_token}"
        return request

    @contextmanager
    def user(self, user_environment_variable):
        """Set the user temporarily."""
        try:
            self.__user_environment_variable = user_environment_variable
            yield
        finally:
            self.__user_environment_variable = None


up_auth = UpAuth()

api = jsonapi_requests.orm.OrmApi.config(
    {
        "API_ROOT": "https://api.up.com.au/api/v1",
        "AUTH": up_auth,
        "VALIDATE_SSL": True,
        "TIMEOUT": 1,
    }
)


class Account(jsonapi_requests.orm.ApiModel):
    """JSON:API model for Up bank accounts."""

    class Meta:
        """JSON:API meta information."""

        type = "accounts"
        api = api

    name = jsonapi_requests.orm.AttributeField("displayName")
    balance = jsonapi_requests.orm.AttributeField("balance")
