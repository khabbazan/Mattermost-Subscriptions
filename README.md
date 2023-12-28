# Mattermost Subscriptions

This Django application is designed as a chat server that integrates with the Mattermost server for managing channels, users, and messages. It employs GraphQL for API interactions and Django Channels for real-time data synchronization using WebSockets. This project also includes a Mattermost proxy module for enhanced functionality.

## Prerequisites
- Python 3.10 or later.
- Django 4.2 or later.
- Graphene 3.3 or later.
- Django Channels 4.0 or later
- A running Mattermost server.

## GraphQL APIs

### Queries
- `UserList`: Retrieve a list of users.
- `ChannelList`: Fetch a list of chat channels.
- `GetMessageList`: Get a list of messages from a channel.

### Mutations
- `UserCreate`: Create a new user.
- `UserGetToken`: Obtain a token for a user.
- `token_auth`: Authenticate and obtain a JSON web token.
- `verify_token`: Verify a user's token.
- `refresh_token`: Refresh a user's token.
- `text_message_send`: Send a text message.
- `channel_create`: Create a new chat channel.

### Subscriptions
- `OnNewChatMessage`: Real-time updates for new chat messages.

### Mattermost Proxy Module
This project features a Mattermost proxy module  based on [python-mattermost-driver](https://github.com/Vaelor/python-mattermost-driver) with two public classes:

#### MattermostAdminProxy
Provides administrative functionalities, like creating/removing users, teams, channels, and managing user statuses and memberships.

#### MattermostUserProxy
Handles user-level interactions with the Mattermost server, such as listing users, teams, channels, sending messages, and joining/leaving channels.

## Features

- Real-time data syncing using Django Channels and Redis.
- GraphQL Subscription for real-time updates in user channels.
- Interaction with Mattermost server for channel and user management.
- Mattermost proxy module for enhanced functionalities.

## Setup and Installation

1. Clone this repository.
2. Create a `.env` file with the following environment variables:
    - `DJANGO_SECRET_KEY`
    - `MATTERMOST_SERVER_URL`
    - `MATTERMOST_ADMIN_LOGIN_ID`
    - `MATTERMOST_ADMIN_LOGIN_PASSWORD`
    - `MATTERMOST_TEAM_IDENTIFIER`
3. Install dependencies: `python -m pip install -r requirements.txt`.
4. Migrate the database: `python manage.py migrate`.
5. Run the server: `python manage.py runserver`.

## Testing and Development Tools

- A JavaScript GraphQL tester client for WebSocket subscription handshake located in the `tester` directory.
- Load testing and development scenarios to ensure robust performance.

## Contributions and License

Contributions are welcome! This project is open-source and licensed under the MIT license. Feel free to fork, contribute, and enhance the functionalities of this integration.

## Contributors

- [Alireza Khabbazan](https://github.com/khabbazan)

---
