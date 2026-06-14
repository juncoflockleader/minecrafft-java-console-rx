import net from "node:net";

// Source RCON protocol packet types.
const TYPE_AUTH = 3;
const TYPE_AUTH_RESPONSE = 2;
const TYPE_EXEC = 2;
const TYPE_RESPONSE = 0;

function encode(id, type, body) {
  const payload = Buffer.from(body, "utf8");
  const buf = Buffer.alloc(payload.length + 14);
  buf.writeInt32LE(payload.length + 10, 0); // length of remainder
  buf.writeInt32LE(id, 4);
  buf.writeInt32LE(type, 8);
  payload.copy(buf, 12);
  // two trailing null bytes (body terminator + packet terminator) already zeroed
  return buf;
}

/**
 * Run a single command against the server over a short-lived RCON connection.
 * Handles multi-packet responses by sending a trailing sentinel packet and
 * concatenating all command-id responses received before the sentinel echo.
 */
function attempt(command, { host, port, password, timeout = 5000 } = {}) {
  const CMD_ID = 1;
  const END_ID = 2;
  return new Promise((resolve, reject) => {
    const socket = net.createConnection({ host, port });
    let buffer = Buffer.alloc(0);
    let authed = false;
    const parts = [];
    let settled = false;

    const timer = setTimeout(() => fail(new Error("RCON timeout")), timeout);

    function done(value) {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      socket.destroy();
      resolve(value);
    }
    function fail(err) {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      socket.destroy();
      reject(err);
    }

    socket.on("connect", () => socket.write(encode(CMD_ID, TYPE_AUTH, password)));
    socket.on("error", fail);
    socket.on("close", () => {
      if (!settled) fail(new Error("RCON connection closed unexpectedly"));
    });

    socket.on("data", (chunk) => {
      buffer = Buffer.concat([buffer, chunk]);
      while (buffer.length >= 4) {
        const len = buffer.readInt32LE(0);
        if (buffer.length < len + 4) break;
        const id = buffer.readInt32LE(4);
        const type = buffer.readInt32LE(8);
        const body = buffer.slice(12, len + 4 - 2).toString("utf8");
        buffer = buffer.slice(len + 4);

        if (!authed) {
          if (type === TYPE_AUTH_RESPONSE) {
            if (id === -1) return fail(new Error("RCON auth failed (bad password)"));
            authed = true;
            socket.write(encode(CMD_ID, TYPE_EXEC, command));
            socket.write(encode(END_ID, TYPE_EXEC, "")); // sentinel
          }
          continue;
        }
        if (type === TYPE_RESPONSE) {
          if (id === END_ID) return done(parts.join(""));
          parts.push(body);
        }
      }
    });
  });
}

/**
 * Run a command with a short-lived RCON connection, retrying once on transient
 * connection errors (the Minecraft RCON listener handles one connection at a
 * time, so rapid back-to-back commands can occasionally drop). Never retries an
 * authentication failure.
 */
export async function rconCommand(command, opts = {}) {
  const { retries = 1, retryDelayMs = 250, ...conn } = opts;
  let lastErr;
  for (let i = 0; i <= retries; i++) {
    try {
      return await attempt(command, conn);
    } catch (err) {
      lastErr = err;
      if (/auth failed/i.test(err.message)) throw err;
      if (i < retries) await new Promise((r) => setTimeout(r, retryDelayMs));
    }
  }
  throw lastErr;
}
