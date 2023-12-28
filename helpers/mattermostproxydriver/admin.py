import re

from django.conf import settings

from helpers.mattermostproxydriver.user import MattermostUserProxy


class MattermostAdminProxy(MattermostUserProxy):
    """
    A subclass of MattermostUserProxy that provides additional administrative functionalities.

    Inherits from MattermostUserProxy and extends its functionalities to include
    administrative tasks such as creating and removing users, teams, and channels, as well as
    managing user's status and membership in teams and channels.

    Inherits Args from MattermostUserProxy:
        base_url (str): The base URL of the Mattermost server.
        login_id (str): The login ID for authenticating with the Mattermost server.
        password (str): The password for authenticating with the Mattermost server.

    Methods:
        create_user: Creates a new user on the Mattermost server with validation of password.
        remove_user: Removes a user from the Mattermost server based on their identifier.
        deactivate_user: Deactivates a user's account on the Mattermost server.
        activate_user: Reactivates a deactivated user's account on the Mattermost server.
        list_all_teams: Lists all teams available on the Mattermost server.
        list_all_public_channels: Lists all public channels for a specified team.
        add_user_to_channel: Adds a user to a specified channel within a specified team.
        create_join_team: Creates a new team with the specified name and joins the authenticated user.
        add_user_to_team: Adds a user to a specified team.
        remove_team: Removes a specified team from the Mattermost server.
        create_join_channel: Creates a new channel within a specified team.
        remove_channel: Removes a specified channel from a team.
    """

    def create_user(self, user_data, exception=True):
        """
        Creates a new user on the Mattermost server with the provided user data.
        Validates the password to meet certain criteria.
        """
        try:
            password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*\W).{10,}$"
            if re.match(password_pattern, user_data.get("password")) is None:
                raise Exception("password should at least 10 chars including uppers, lowers, numbers and symbols")

            username_pattern = r"^[a-z][a-z0-9._-]{2,21}$"
            if re.fullmatch(username_pattern, user_data.get("username")) is None:
                raise Exception("Username must begin with a letter, and contain between 3 to 22 lowercase characters made up of numbers, letters, and the symbols")

            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if re.fullmatch(email_pattern, user_data.get("email")) is None:
                raise Exception("Invalid email address")

            response = self.driver.users.create_user(user_data)
            if response.get("id", False):
                return {"name": response["username"], "id": response["id"]}
            return False
        except Exception as e:
            if exception:
                raise e
            return False

    def deactivate_user(self, user_identifier, exception=True):
        """
        Deactivates a user's account on the Mattermost server.
        """
        try:
            user_id = self._find_user_id_or_name(user_identifier) if not user_identifier.isdigit() else user_identifier
            if user_id is None:
                raise Exception("User identifier not found.")

            response = self.driver.users.deactivate_user(user_id)
            return response["status"] == "OK"
        except Exception as e:
            if exception:
                raise e
            return False

    def activate_user(self, user_identifier, exception=True):
        """
        Reactivates a deactivated user's account on the Mattermost server.
        """
        try:
            user_id = self._find_user_id_or_name(user_identifier) if not user_identifier.isdigit() else user_identifier
            if user_id is None:
                raise Exception("User identifier not found.")

            response = self.driver.users.update_user_active_status(user_id, options={"active": True})
            return response["status"] == "OK"
        except Exception as e:
            if exception:
                raise e
            return False

    def list_all_teams(self, exception=True):
        """
        Lists all teams available on the Mattermost server.
        """
        try:
            teams = self.driver.teams.get_teams()
            return [{"name": team["name"], "id": team["id"]} for team in teams]
        except Exception as e:
            if exception:
                raise e
            return False

    def list_all_public_channels(self, team_identifier=settings.MATTERMOST_SERVER["team_identifier"], exception=True):
        """
        Lists all public channels for a specified team.
        """
        try:
            team_id = self._find_team_id(team_identifier) if not team_identifier.isdigit() else team_identifier
            if team_id is None:
                raise Exception("Team identifier not found.")

            channels = self.driver.channels.get_public_channels(team_id=team_id)
            return [{"team_name": team_identifier, "name": channel["name"], "id": channel["id"]} for channel in channels if channel["display_name"]]
        except Exception as e:
            if exception:
                raise e
            return False

    def add_user_to_channel(self, channel_identifier, user_identifier, team_identifier=settings.MATTERMOST_SERVER["team_identifier"], exception=True):
        """
        Adds a user to a specified channel within a specified team.
        """
        try:
            team_id = self._find_team_id(team_identifier) if not team_identifier.isdigit() else team_identifier
            if team_id is None:
                raise Exception("Team identifier not found.")

            channel_id = self._find_channel_id(team_id, channel_identifier) if not channel_identifier.isdigit() else channel_identifier
            if channel_id is None:
                raise Exception("Channel identifier not found.")

            user_id = self._find_user_id_or_name(user_identifier) if not user_identifier.isdigit() else user_identifier
            if user_id is None:
                raise Exception("User identifier not found.")

            response = self.driver.channels.add_user(channel_id=channel_id, options={"user_id": user_id})
            return response is not None
        except Exception as e:
            if exception:
                raise e
            return False

    def create_join_team(self, team_name, exception=True):
        """
        Creates a new team with the specified name and automatically joins the authenticated user.
        Validates the team name to ensure it meets certain criteria.
        """
        try:
            team_name_pattern = r"[^A-Za-z0-9-]"
            if re.search(team_name_pattern, team_name):
                raise Exception("Team name could not contains symbols or underscores.")

            if self._find_team_id(identifier=team_name) is not None:
                raise Exception("Team is already exist.")

            data = {"name": team_name, "display_name": team_name, "type": "O"}
            response = self.driver.teams.create_team(options=data)
            return "id" in response
        except Exception as e:
            if exception:
                raise e
            return False

    def add_user_to_team(self, user_identifier, team_identifier=settings.MATTERMOST_SERVER["team_identifier"], exception=True):
        """
        Adds a user to a specified team.
        """
        try:
            team_id = self._find_team_id(team_identifier) if not team_identifier.isdigit() else team_identifier
            if team_id is None:
                raise Exception("Team identifier not found.")

            user_id = self._find_user_id_or_name(user_identifier) if not user_identifier.isdigit() else user_identifier
            if user_id is None:
                raise Exception("User identifier not found.")

            data = {"team_id": team_id, "user_id": user_id}
            response = self.driver.teams.add_user_to_team(team_id, options=data)
            return response is not None
        except Exception as e:
            if exception:
                raise e
            return False

    def remove_team(self, team_identifier, exception=True):
        """
        Removes a specified team from the Mattermost server.
        """
        try:
            team_id = self._find_team_id(team_identifier) if not team_identifier.isdigit() else team_identifier
            if team_id is None:
                raise Exception("Team identifier not found.")

            response = self.driver.teams.delete_team(team_id=team_id, params={"permanent": True})
            return response["status"] == "OK"
        except Exception as e:
            if exception:
                raise e
            return False

    def create_join_channel(self, channel_name, team_identifier=settings.MATTERMOST_SERVER["team_identifier"], exception=True):
        """
        Creates a new channel within a specified team and automatically joins the authenticated user.
        Validates the channel name to ensure it meets certain criteria.
        """
        try:
            team_id = self._find_team_id(team_identifier) if not team_identifier.isdigit() else team_identifier
            if team_id is None:
                raise Exception("Team identifier not found.")

            channel_id = self._find_channel_id(team_id=team_id, identifier=channel_name)
            if channel_id:
                raise Exception("Channel is already exist.")

            data = {"team_id": team_id, "name": channel_name, "display_name": channel_name, "type": "O"}
            response = self.driver.channels.create_channel(data)
            return response["id"]
        except Exception as e:
            if exception:
                raise e
            return False

    def remove_channel(self, channel_identifier, team_identifier=settings.MATTERMOST_SERVER["team_identifier"], exception=True):
        """
        Removes a specified channel from a specified team.
        """
        try:
            team_id = self._find_team_id(team_identifier) if not team_identifier.isdigit() else team_identifier
            if team_id is None:
                raise Exception("Team identifier not found.")

            channel_id = self._find_channel_id(team_id, channel_identifier) if not channel_identifier.isdigit() else channel_identifier
            if channel_id is None:
                raise Exception("Channel identifier not found.")

            response = self.driver.channels.delete_channel(channel_id)
            return response["status"] == "OK"
        except Exception as e:
            if exception:
                raise e
            return False
