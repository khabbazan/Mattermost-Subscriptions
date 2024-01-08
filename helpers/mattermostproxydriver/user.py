from datetime import datetime

import pytz
from django.conf import settings
from mattermostdriver import Driver


class MattermostUserProxy:
    """
     A proxy class for interacting with a Mattermost server as a User.

    This class provides methods for various operations on a Mattermost server,
    such as listing users, teams, channels, joining channels, sending messages, and more.
    It uses the Mattermost Driver to communicate with the Mattermost API.

    Args:
        base_url (str): Base URL of the Mattermost server.
        login_id (str): Login ID for authenticating with the Mattermost server.
        password (str): Password for authenticating with the Mattermost server.

    Methods:
        list_users: Lists all users from the Mattermost server.
        list_related_teams: Lists teams related to the authenticated user.
        list_related_channels: Lists channels related to a specific team, with an option to filter by the authenticated user.
        join_to_channel: Joins the authenticated user to a specified channel.
        leave_from_channel: Removes the authenticated user from a specified channel.
        send_message: Sends a message to a specified channel.
        get_messages: Retrieves messages from a specified channel, optionally converting timestamps to a given timezone.
    """

    def __init__(
        self,
        login_id=settings.MATTERMOST_SERVER["admin_login_id"],
        password=settings.MATTERMOST_SERVER["admin_password"],
        base_url=settings.MATTERMOST_SERVER["server_URL"],
    ):
        """
        Initializes the MattermostUserProxy instance with server details and admin token.
        """
        self.base_url = base_url
        self.driver = Driver({"url": base_url, "login_id": login_id, "password": password, "scheme": "https", "port": 443, "basepath": "/api/v4", "verify": True})
        self.driver.login()
        self.headers = {"Authorization": f"Bearer {self.driver.client.token}", "Content-Type": "application/json"}
        self.username = self.driver.client.username
        self.userid = self.driver.client.userid

    def _find_by_id_or_name(self, collection, identifier, find_name=False):
        """
        Searches for an item by ID or name in a given collection.
        """
        for item in collection:
            if item.get("id") == identifier or item.get("name") == identifier or item.get("username") == identifier:
                if find_name:
                    return item.get("username") if "username" in item else item.get("id")
                else:
                    return item.get("id") if "id" in item else item.get("username")
        return None

    def _find_user_id_or_name(self, identifier, find_name=False):
        """
        Finds a user ID based on a provided identifier (ID or username).
        """
        if find_name:
            return self._find_by_id_or_name(self.driver.users.get_users(), identifier, find_name=True)
        else:
            return self._find_by_id_or_name(self.driver.users.get_users(), identifier)

    def _find_channel_id(self, team_id, identifier):
        """
        Finds a channel ID within a specified team based on the channel identifier.
        """
        return self._find_by_id_or_name(self.driver.channels.get_channels_for_user(user_id=self.userid, team_id=team_id), identifier)

    def _find_team_id(self, identifier):
        """
        Finds a team ID based on a provided team identifier (ID or team name).
        """
        return self._find_by_id_or_name(self.driver.teams.get_user_teams(self.userid), identifier)

    @staticmethod
    def convert_timestamp_to_iso(timestamp, tz_name):
        """
        Converts a timestamp to ISO format in a specified timezone.
        """
        utc_time = datetime.utcfromtimestamp(timestamp / 1000).replace(tzinfo=pytz.utc)
        target_time = utc_time.astimezone(pytz.timezone(tz_name))
        return target_time.isoformat()

    def list_users(self):
        """
        Lists all users from the Mattermost server.
        """
        users = self.driver.users.get_users()
        return [{"name": user["username"], "id": user["id"]} for user in users]

    def list_related_teams(self):
        """
        Lists teams related to the authenticated user.
        """
        teams = self.driver.teams.get_user_teams(user_id=self.userid)
        return [{"name": team["name"], "id": team["id"]} for team in teams]

    def list_related_channels(self, team_identifier=settings.MATTERMOST_SERVER["team_identifier"], exclude_list=None, params=None, exception=True):
        """
        Lists channels related to a specific team, excluding those that contain any of the specified strings in the list,
        with pagination. Each channel's data includes the last message of the channel.
        """
        if exclude_list is None:
            exclude_list = []

        team_id = self._find_team_id(team_identifier)
        if team_id is None:
            if exception:
                raise Exception("Team identifier not found.")
            return False

        channels = self.driver.channels.get_channels_for_user(user_id=self.userid, team_id=team_id)

        # Converting all strings in the exclude list to lowercase for case-insensitive comparison
        exclude_list = [str.lower() for str in exclude_list]

        # Fetching channels and their last messages
        filtered_channels = []
        for channel in channels:
            if channel["display_name"] and not any(exclude_str in channel["name"].lower() for exclude_str in exclude_list):
                # Fetch the messages of the channel and get the last one
                # This is a placeholder - replace with actual method to fetch messages and then get the last message
                last_message, _, _ = self.get_messages(team_identifier=team_identifier, channel_identifier=channel["name"], last_message=True)

                filtered_channels.append(
                    {
                        "team_name": team_identifier,
                        "name": channel["name"],
                        "id": channel["id"],
                        "last_message": last_message[0],  # Including the last message in the channel data
                    }
                )

        # Pagination
        has_next = False
        if params.get("page", False) and params.get("per_page", False):
            page_number = int(params.get("page"))
            page_size = int(params.get("per_page"))
            start_index = (page_number - 1) * page_size
            end_index = start_index + page_size

            # Slicing the list for the requested page
            paginated_channels = filtered_channels[start_index:end_index]

            # Calculate total items and total pages
            total_items = len(filtered_channels)
            total_pages = -(-total_items // page_size)  # Ceiling division

            # Determine if there is a next page
            has_next = page_number < total_pages

        else:
            paginated_channels = filtered_channels

        return paginated_channels, has_next

    def join_to_channel(self, channel_identifier, team_identifier=settings.MATTERMOST_SERVER["team_identifier"], exception=True):
        """
        Joins the authenticated user to a specified channel.
        """
        try:
            team_id = self._find_team_id(team_identifier)
            if team_id is None:
                raise Exception("Team identifier not found.")

            channel_id = self._find_channel_id(team_id, channel_identifier)
            if channel_id is None:
                raise Exception("Channel identifier not found.")

            response = self.driver.channels.add_user(channel_id, options={"user_id": self.userid})
            return response is not None
        except Exception as e:
            if exception:
                raise e
            return False

    def leave_from_channel(self, channel_identifier, team_identifier=settings.MATTERMOST_SERVER["team_identifier"], exception=True):
        """
        Removes the authenticated user from a specified channel.
        """
        try:
            team_id = self._find_team_id(team_identifier)
            if team_id is None:
                raise Exception("Team identifier not found.")

            channel_id = self._find_channel_id(team_id, channel_identifier)
            if channel_id is None:
                raise Exception("Channel identifier not found.")

            response = self.driver.channels.remove_channel_member(channel_id, self.userid)
            return response["status"] == "OK"
        except Exception as e:
            if exception:
                raise e
            return False

    def send_message(self, channel_identifier, message, team_identifier=settings.MATTERMOST_SERVER["team_identifier"], time_zone=settings.TIME_ZONE, exception=True):
        """
        Sends a message to a specified channel.
        """
        try:
            team_id = self._find_team_id(team_identifier)
            if team_id is None:
                raise Exception("Team identifier not found.")

            channel_id = self._find_channel_id(team_id, channel_identifier)
            if channel_id is None:
                raise Exception("Channel identifier not found.")

            post = {"channel_id": channel_id, "message": message}
            response = self.driver.posts.create_post(post)

            formatted_response = {
                "message": response["message"],
                "create_at": self.convert_timestamp_to_iso(response["create_at"], time_zone) if time_zone else response["create_at"],
                "user_id": response["user_id"],
                "username": self._find_user_id_or_name(response["user_id"], find_name=True),
                "id": response["id"],
                "type": response["type"] if response["type"] else "str",
            }

            return formatted_response
        except Exception as e:
            if exception:
                raise e
            return False

    def get_messages(
        self,
        channel_identifier,
        team_identifier=settings.MATTERMOST_SERVER["team_identifier"],
        time_zone=settings.TIME_ZONE,
        last_message=False,
        params=None,
        exception=True,
    ):
        """
        Retrieves messages from a specified channel, optionally converting timestamps to a given timezone.
        If 'last_message' is True, only the last message is returned.
        """
        try:
            team_id = self._find_team_id(team_identifier)
            if team_id is None:
                raise Exception("Team identifier not found.")

            channel_id = self._find_channel_id(team_id, channel_identifier)
            if channel_id is None:
                raise Exception("Channel identifier not found.")

            if last_message:
                # Fetch only the last message
                messages = self.driver.posts.get_posts_for_channel(channel_id, params={"page": 0, "per_page": 1})
            else:
                # Fetch all messages (or a specific page if pagination parameters are provided)
                messages = self.driver.posts.get_posts_for_channel(channel_id, params=params)

            # Formatting messages
            formatted_messages = [
                {
                    "message": msg["message"],
                    "create_at": self.convert_timestamp_to_iso(msg["create_at"], time_zone) if time_zone else msg["create_at"],
                    "user_id": msg["user_id"],
                    "username": self._find_user_id_or_name(msg["user_id"], find_name=True),
                    "id": msg["id"],
                    "type": msg["type"] if msg["type"] else "str",
                }
                for msg in messages["posts"].values()
            ]

            return formatted_messages, bool(messages["prev_post_id"]), bool(messages["next_post_id"])
        except Exception as e:
            if exception:
                raise e
            return [], False, False
