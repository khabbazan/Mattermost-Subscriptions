import graphene
from graphql_jwt.decorators import login_required

from apps.chat.gql.types import ChannelListType
from apps.chat.gql.types import MessageListType
from helpers.generic_types import PageType
from helpers.mattermostproxydriver.user import MattermostUserProxy

class ChannelList(graphene.ObjectType):
    """
    GraphQL ObjectType for listing channels.
    This class provides the functionality to query a list of channels associated with a user with pagination support.
    """

    channel_list = graphene.Field(
        ChannelListType,
        page=graphene.Argument(PageType, description="Pagination details including page size and page number."),
        description="Query to retrieve a paginated list of channels."
    )

    @login_required
    def resolve_channel_list(self, info, **kwargs):
        """
        Resolver for the channel_list query.
        Retrieves a list of channels based on pagination parameters. Requires user authentication.

        Args:
            info (ResolveInfo): Information about the query.
            **kwargs: Keyword arguments containing pagination details.

        Returns:
            ChannelListType: A paginated list of channels with an indication of whether there are more pages.
        """
        user = info.context.user
        page = kwargs.get("page", {"page_size": 10, "page_number": 0})

        matter_user = MattermostUserProxy(login_id=user.username, password=user.password[:30])
        data, has_next = matter_user.list_related_channels(exclude_list=[], params={"page": page["page_number"], "per_page": page["page_size"]})

        channel_list = ChannelListType(data=data, has_next=has_next)

        return channel_list


class GetMessageList(graphene.ObjectType):
    """
    GraphQL ObjectType for retrieving a list of messages.
    This class allows querying a list of messages from a specific channel with pagination support.
    """

    get_message_list = graphene.Field(
        MessageListType,
        channel_identifier=graphene.Argument(graphene.String, required=True, description="Identifier of the channel to retrieve messages from."),
        page=graphene.Argument(PageType, description="Pagination details including page size and page number."),
        description="Query to retrieve a paginated list of messages from a specified channel."
    )

    @login_required
    def resolve_get_message_list(self, info, **kwargs):
        """
        Resolver for the get_message_list query.
        Retrieves a list of messages from a specified channel based on pagination parameters. Requires user authentication.

        Args:
            info (ResolveInfo): Information about the query.
            **kwargs: Keyword arguments containing the channel identifier and pagination details.

        Returns:
            MessageListType: A paginated list of messages with indications of previous and next pages.
        """
        user = info.context.user
        page = kwargs.get("page", {"page_size": 10, "page_number": 0})
        channel_identifier = kwargs.get("channel_identifier", None)

        matter_user = MattermostUserProxy(login_id=user.username, password=user.password[:30])
        data, has_prev, has_next = matter_user.get_messages(channel_identifier=channel_identifier, params={"page": page["page_number"], "per_page": page["page_size"]})

        message_list = MessageListType(data=data, has_previous=has_prev, has_next=has_next)

        return message_list
