import graphene
from django.contrib.auth.models import User
from django.core.handlers.asgi import ASGIRequest

from apps.account.gql.types import UserQueryType


class MessageQueryType(graphene.ObjectType):
    """
    GraphQL type representing a message in a chat system.
    """

    id = graphene.String(description="Unique identifier of the message.")

    def resolve_id(root, info):
        """Resolve the message ID."""
        return root["id"]

    message = graphene.String(description="Content of the message.")

    def resolve_message(root, info):
        """Resolve the message content, with special handling for system messages."""
        if root["type"] == "system_join_team":
            return "Welcome"
        return root["message"]

    create_at = graphene.String(description="Timestamp when the message was created.")

    def resolve_create_at(root, info):
        """Resolve the creation timestamp of the message."""
        return root["create_at"]

    owner = graphene.Field(UserQueryType, description="User who sent the message.")

    def resolve_owner(root, info):
        """Resolve the owner (sender) of the message."""
        if isinstance(info.context, ASGIRequest):
            return User.objects.filter(username=root["username"]).first()
        else:
            return User.objects.filter(username=root["username"]).afirst()

    type = graphene.String(description="Type of the message, e.g., 'text', 'image', 'system_join_team'.")

    def resolve_type(root, info):
        """Resolve the type of the message."""
        return root["type"]


class MessageListType(graphene.ObjectType):
    """
    GraphQL type representing a paginated list of messages.
    """

    data = graphene.List(MessageQueryType, description="List of messages.")
    has_next = graphene.Boolean(description="Indicates if there are more pages available.")
    has_previous = graphene.Boolean(description="Indicates if there are previous pages available.")


class ChannelQueryType(graphene.ObjectType):
    """
    GraphQL type representing a chat channel.
    """

    channel_id = graphene.String(description="Unique identifier of the chat channel.")

    def resolve_channel_id(root, info):
        """Resolve the channel ID."""
        return root["id"]

    channel_name = graphene.String(description="Name of the chat channel.")

    def resolve_channel_name(root, info):
        """Resolve the name of the chat channel."""
        return root["name"]

    last_message = graphene.Field(MessageQueryType, description="The last message sent in the channel.")

    def resolve_last_message(root, info):
        """Resolve the last message sent in the channel."""
        return root["last_message"]


class ChannelListType(graphene.ObjectType):
    """
    GraphQL type representing a paginated list of chat channels.
    """

    data = graphene.List(ChannelQueryType, description="List of chat channels.")
    has_next = graphene.Boolean(description="Indicates if there are more pages available.")
