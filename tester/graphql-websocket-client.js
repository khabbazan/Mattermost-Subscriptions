const WebSocket = require('ws');

const ws = new WebSocket("ws://localhost:8000/ws/graphql/", "graphql-ws");

ws.onopen = () => {
  const authMessage = {
    type: 'connection_init',
    payload: {
      headers: {
        Authorization: 'JWT YOUR_TOKEN_HERE'
      }
    }
  };
  ws.send(JSON.stringify(authMessage));

  const subscriptionQuery = `
    subscription subs {
      onNewChatMessage(chatroom: "lovely") {
        text
      }
    }
  `;
  const message = {
    id: '1',
    type: 'start',
    payload: {
      query: subscriptionQuery
    }
  };
  ws.send(JSON.stringify(message));
};

ws.onmessage = function(event) {
  console.log("Received:", event.data);
};

ws.onerror = function(error) {
  console.error("WebSocket Error:", error);
};

ws.onclose = function() {
  console.log("Connection closed");
};
