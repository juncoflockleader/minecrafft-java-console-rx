import net from "node:net";

// Minecraft Server List Ping (modern handshake) — returns server status JSON.
function writeVarInt(value) {
  const bytes = [];
  let v = value >>> 0;
  do {
    let b = v & 0x7f;
    v >>>= 7;
    if (v !== 0) b |= 0x80;
    bytes.push(b);
  } while (v !== 0);
  return Buffer.from(bytes);
}

function readVarInt(buf, offset) {
  let num = 0;
  let shift = 0;
  let pos = offset;
  while (true) {
    if (pos >= buf.length) return null; // need more data
    const b = buf[pos++];
    num |= (b & 0x7f) << shift;
    if ((b & 0x80) === 0) break;
    shift += 7;
  }
  return { value: num >>> 0, size: pos - offset };
}

function packet(...buffers) {
  const body = Buffer.concat(buffers);
  return Buffer.concat([writeVarInt(body.length), body]);
}

export function pingStatus({ host, port, timeout = 4000 } = {}) {
  return new Promise((resolve, reject) => {
    const socket = net.createConnection({ host, port });
    let buffer = Buffer.alloc(0);
    let settled = false;
    const timer = setTimeout(() => fail(new Error("status ping timeout")), timeout);

    function fail(err) {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      socket.destroy();
      reject(err);
    }
    function ok(value) {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      socket.destroy();
      resolve(value);
    }

    socket.on("connect", () => {
      const addr = Buffer.from(host, "utf8");
      // Handshake: id, protocol version, address, port, next state (1 = status).
      const hs = packet(
        writeVarInt(0x00),
        writeVarInt(0), // protocol version 0 = "any"
        writeVarInt(addr.length),
        addr,
        Buffer.from([(port >> 8) & 0xff, port & 0xff]),
        writeVarInt(1), // next state: status
      );
      socket.write(hs);
      socket.write(packet(writeVarInt(0x00))); // status request
    });

    socket.on("data", (chunk) => {
      buffer = Buffer.concat([buffer, chunk]);
      // Parse: [packetLen][packetId=0][jsonLen][json...]
      const lenField = readVarInt(buffer, 0);
      if (!lenField) return;
      const total = lenField.value + lenField.size;
      if (buffer.length < total) return; // wait for more
      let pos = lenField.size;
      const idField = readVarInt(buffer, pos);
      pos += idField.size;
      const strLen = readVarInt(buffer, pos);
      pos += strLen.size;
      if (buffer.length < pos + strLen.value) return;
      const json = buffer.slice(pos, pos + strLen.value).toString("utf8");
      try {
        const d = JSON.parse(json);
        const desc = d.description;
        const motd = typeof desc === "string" ? desc : desc?.text ?? extractMotd(desc) ?? "";
        ok({
          online: true,
          version: d.version?.name ?? null,
          protocol: d.version?.protocol ?? null,
          players: { online: d.players?.online ?? 0, max: d.players?.max ?? 0 },
          motd,
        });
      } catch (e) {
        fail(e);
      }
    });

    socket.on("error", fail);
  });
}

function extractMotd(desc) {
  if (!desc) return "";
  let out = desc.text ?? "";
  if (Array.isArray(desc.extra)) out += desc.extra.map((e) => (typeof e === "string" ? e : e.text ?? "")).join("");
  return out;
}
