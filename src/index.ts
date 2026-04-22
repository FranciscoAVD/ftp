import { DEFAULT_CONNECTION_PORT } from "./config";

// DOCS: https://bun.com/docs/runtime/networking/tcp
Bun.listen({
  hostname: "localhost",
  port: DEFAULT_CONNECTION_PORT,
  socket: {
    open(socket) {},
    close(socket) {},
    error(socket) {},
    data(socket, data) {},
  },
  //SFTP beyond scope.
  tls: false,
});
