import graphene

from apps.chat.gql.types import MessageQueryType
from helpers import channels_graphql_ws


class OnNewChatMessage(channels_graphql_ws.Subscription):
    """
    GraphQL Subscription for new chat messages.
    This subscription allows clients to listen for new messages on a specified channel.
    """

    channel_identifier = graphene.String()
    message = graphene.Field(MessageQueryType)

    class Arguments:
        channel_identifier = graphene.String(required=True, description="The identifier of the chat channel to subscribe to.")

    @staticmethod
    def subscribe(root, info, channel_identifier):
        """
        Called when a user subscribes to the subscription.

        Args:
            root (Object): Root object, not used in this subscription.
            info (ResolveInfo): Information about the subscription.
            channel_identifier (str): Identifier of the channel to subscribe to.

        Returns:
            list: A list containing the channel identifier.

        Raises:
            Exception: If the user is not authenticated.
        """
        user = info.context.channels_scope["user"]
        # Check if the user is authenticated
        if not user or not user.is_authenticated:
            # Reject the subscription if the user is not authenticated
            raise Exception("User is not authenticated.")

        print("new user has subscribed via ws.", channel_identifier)
        return [channel_identifier]

    def publish(self, info, channel_identifier=None):
        """
        Called to prepare the subscription notification message.

        Args:
            info (ResolveInfo): Information about the subscription.
            channel_identifier (str): The identifier of the channel.

        Returns:
            OnNewChatMessage: The subscription object with the new message.
        """
        # The `self` contains payload delivered from the `broadcast()`.
        new_msg_channel_identifier = self["channel_identifier"]
        new_msg = self["message"]

        # Ensure that the published message is for the subscribed channel
        assert channel_identifier is None or channel_identifier == new_msg_channel_identifier

        return OnNewChatMessage(channel_identifier=channel_identifier, message=new_msg)

    @classmethod
    async def new_chat_message(cls, channel_identifier, message):
        """
        Auxiliary function to send subscription notifications.

        This method encapsulates the broadcast invocation, allowing the payload structure to be considered as an implementation detail.

        Args:
            channel_identifier (str): The identifier of the channel where the message is sent.
            message (dict): The message to be sent.
        """
        await cls.broadcast(
            group=channel_identifier,
            payload={"channel_identifier": channel_identifier, "message": message},
        )
