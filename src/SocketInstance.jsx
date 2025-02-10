import { io } from "socket.io-client";

const protocol = window.location.protocol; // 'http:' or 'https:'
const host = window.location.hostname; // Gets the domain name or IP
const port = 8001;
const socketPath = "/socket.io/"; // Matches your Caddy reverse proxy path
export  const socketURL = `ws://${host}:${port}`; // If no port, use `${protocol}//${host}`
// export const socketURL = `ws://${host}`;

const socketConfig = {
  path: socketPath,
  transports: ["websocket", "polling"],
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  timeout: 10000,
};

let socket;

export const getSocket = () => {
  if (!socket) {
    socket = io(socketURL, socketConfig);
  }
  return socket;
};
