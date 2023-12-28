from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from graphql_jwt.utils import jwt_decode


class JWTwsAuthMiddleware(BaseMiddleware):
    """
    Middleware for WebSocket authentication using JWT.
    Parses the JWT token from the WebSocket headers to authenticate the user.
    """

    async def __call__(self, scope, receive, send):
        """
        Asynchronous middleware call to handle scope modification for WebSocket connections.

        Args:
            scope (dict): The connection scope containing headers and other connection details.
            receive (callable): Receive function for the WebSocket.
            send (callable): Send function for the WebSocket.
        """
        headers = dict(scope["headers"])
        if b"authorization" in headers:
            try:
                # Decode the JWT token and retrieve the user
                token_name, token_key = headers[b"authorization"].decode().split()
                if token_name == "JWT":
                    decoded_data = jwt_decode(token_key)
                    scope["user"] = await self.get_user(decoded_data["username"])
            except Exception:
                # In case of any exception, continue without modifying the scope
                pass
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, username):
        """
        Asynchronously retrieve the user from the database based on the username.

        Args:
            username (str): Username of the user to be retrieved.

        Returns:
            User: The user object if exists, otherwise AnonymousUser.
        """
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return AnonymousUser()
