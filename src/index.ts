import { DEFAULT_CONNECTION_PORT } from "./config";

// DOCS: https://bun.com/docs/runtime/networking/tcp
try {
  Bun.listen({
    hostname: "localhost",
    port: DEFAULT_CONNECTION_PORT,
    socket: {
      open(socket) {
        console.log("Client connected.");
      },
      close(socket) {
        console.log("Connection closed.");
      },
      error(socket, err) {
        console.log(err);
      },
      data(socket, data) {},
    },
    //SFTP beyond scope.
    tls: false,
  });
} catch (err) {
  if (err instanceof Error) console.error(err.message);
  else console.error(`Failed to start server. ${err}`);
}
