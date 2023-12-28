import json
import graphene
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from graphql_jwt.decorators import login_required
from django.contrib.auth.models import User

from apps.chat.gql.subscriptions import OnNewChatMessage
from helpers import http_code
from helpers.generic_types import ResponseBase
from helpers.mattermostproxydriver.user import MattermostUserProxy
from helpers.mattermostproxydriver.admin import MattermostAdminProxy

class ChannelCreate(graphene.Mutation):
    """
    Mutation to create a new channel.
    This mutation is responsible for creating a new channel in the system and adding specified members to it.
    """

    class Arguments:
        channel_name = graphene.Argument(graphene.String, required=True, description="Name of the channel to be created.")
        members = graphene.Argument(graphene.List(graphene.String), required=True, description="List of usernames to be added to the channel.")

    Output = ResponseBase

    @login_required
    def mutate(self, info, channel_name, members):
        """
        Creates a new channel with the given name and adds the specified members to it.

        Args:
            info (ResolveInfo): Information about the mutation.
            channel_name (str): Name of the channel to create.
            members (list of str): Usernames of members to add to the channel.

        Returns:
            ResponseBase: The result of the channel creation operation.
        """
        user = info.context.user
        member_users = [
            User.objects.filter(username__iexact=username).first()
            for username in members
        ]

        if None in member_users:
            raise Exception("Members are not valid.")

        matter_admin = MattermostAdminProxy()
        channel_id = matter_admin.create_join_channel(channel_name=channel_name)
        for u in member_users + [user]:
            matter_admin.add_user_to_channel(channel_identifier=channel_name, user_identifier=u.username)

        if channel_id:
            return ResponseBase(
                status=http_code.HTTP_200_OK,
                status_code=http_code.HTTP_200_OK_CODE,
                message="Channel created successfully!",
                metadata={"channel_id": channel_id},
            )
        else:
            return ResponseBase(
                status=http_code.HTTP_400_BAD_REQUEST_CODE,
                status_code=http_code.HTTP_400_BAD_REQUEST_CODE,
                message="Channel creation failed!",
            )

class TextMessageSend(graphene.Mutation):
    """
    Mutation to send a text message to a channel.
    This mutation handles sending a message to a specified channel and broadcasts it to all channel members.
    """

    class Arguments:
        channel_identifier = graphene.Argument(graphene.String, required=True, description="Identifier of the channel to send the message to.")
        text_message = graphene.Argument(graphene.String, required=True, description="Text message to be sent.")

    Output = ResponseBase

    @login_required
    def mutate(self, info, channel_identifier, text_message):
        """
        Sends a text message to a specified channel.

        Args:
            info (ResolveInfo): Information about the mutation.
            channel_identifier (str): Identifier of the channel.
            text_message (str): The text message to be sent.

        Returns:
            ResponseBase: The result of the message sending operation.
        """
        user = info.context.user
        matter_user = MattermostUserProxy(login_id=user.username, password=user.password[:30])
        response = matter_user.send_message(channel_identifier=channel_identifier, message=text_message)

        formatted_response = {
            "id": response.get("id", None),
            "message": response.get('message', None),
            "create_at": response.get('create_at', None),
            "username": response.get("username", None),
            "type": response.get('type', None),
        }

        async_to_sync(OnNewChatMessage.new_chat_message)(
            channel_identifier=channel_identifier, message=formatted_response
        )

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_add)(
            channel_identifier,
            channel_identifier,
        )

        # Prepare the message
        message = {
            "type": "chat_message",
            "message": json.dumps({"channel_identifier": channel_identifier, "message": formatted_response})
        }

        # Broadcast the message to the group
        async_to_sync(channel_layer.group_send)(channel_identifier, message)

        if formatted_response.get("id", None):
            return ResponseBase(
                status=http_code.HTTP_200_OK,
                status_code=http_code.HTTP_200_OK_CODE,
                message="Message send successfully!",
                metadata={"message_id": formatted_response["id"]},
            )
        else:
            return ResponseBase(
                status=http_code.HTTP_400_BAD_REQUEST_CODE,
                status_code=http_code.HTTP_400_BAD_REQUEST_CODE,
                message="Message send failed!",
            )
