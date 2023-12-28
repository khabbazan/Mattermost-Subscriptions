import math
import graphene
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from graphql_jwt.decorators import login_required

from apps.account.gql.types import UserListType
from helpers.generic_types import PageType


class UserList(graphene.ObjectType):
    """
    GraphQL ObjectType for listing users.
    This class provides the functionality to query a list of users with pagination support.
    """

    user_list = graphene.Field(
        UserListType,
        page=graphene.Argument(PageType, description="Pagination details including page size and page number."),
        description="Query to retrieve a paginated list of users."
    )

    @login_required
    def resolve_user_list(root, info, **kwargs):
        """
        Resolver for the user_list query.
        Retrieves a list of users based on pagination parameters. Requires user authentication.

        Args:
            root (Object): Root object, not used in this query.
            info (ResolveInfo): Information about the query.
            **kwargs: Keyword arguments containing pagination details.

        Returns:
            UserListType: A paginated list of users along with total page count and user count.
        """

        result = User.objects.all()

        # Extracting pagination details from kwargs with default values
        page = kwargs.get("page", {"page_size": 10, "page_number": 1})
        page_number = page.get("page_number")
        page_size = page.get("page_size")

        # Paginating the result set
        response = Paginator(result, page_size)
        page_count = math.ceil(result.count() / page_size)  # Calculating the total number of pages
        count = result.count()  # Total number of users

        # Constructing the UserListType with paginated data
        user_list = UserListType(data=response.page(page_number), page_count=page_count, count=count)

        return user_list
