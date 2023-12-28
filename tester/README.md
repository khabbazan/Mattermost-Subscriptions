# GraphQL WebSocket Client

This document explains how to use a JavaScript WebSocket client to connect to a GraphQL subscription endpoint. The code includes a mechanism to send an authorization token as part of the initial connection payload, which mimics the behavior of HTTP headers in WebSocket communication.

## Code Description

The JavaScript code provided establishes a WebSocket connection to a GraphQL server. It sends an authentication message with an authorization token immediately after the connection opens. Then, it subscribes to a specific GraphQL subscription. The client listens for messages from the server and logs them to the console.

## Prerequisites

- Ensure you have Node.js installed on your system.
- The `ws` package is required to run this code in a Node.js environment since native WebSocket support is generally available only in browser environments.

## Installation

1. Create a new directory for your project.
2. Initialize a new Node.js project:
   ```bash
   npm init -y
   ```
3. Install the ws package:
    ```bash
   npm install ws
    ```

## Running the Script

Run the script using Node.js:

```bash
node graphql-websocket-client.js
```

Replace `ws://localhost:8000/ws/graphql/` with your GraphQL WebSocket endpoint and `YOUR_TOKEN_HERE` with your actual authorization token.
