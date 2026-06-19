import crypto from "node:crypto";

// Constant-time credential comparison.
function safeEqual(a, b) {
  const ab = Buffer.from(a);
  const bb = Buffer.from(b);
  if (ab.length !== bb.length) return false;
  return crypto.timingSafeEqual(ab, bb);
}

function check(authHeader, user, password) {
  if (!authHeader?.startsWith("Basic ")) return false;
  let decoded;
  try {
    decoded = Buffer.from(authHeader.slice(6), "base64").toString("utf8");
  } catch {
    return false;
  }
  const idx = decoded.indexOf(":");
  if (idx === -1) return false;
  return safeEqual(decoded.slice(0, idx), user) && safeEqual(decoded.slice(idx + 1), password);
}

// Stable per-credential token (survives restarts; never the raw password).
function authToken(user, password) {
  return crypto.createHash("sha256").update(`${user}:${password}`).digest("hex");
}

function cookieValue(req, name) {
  const raw = req.headers.cookie || "";
  for (const part of raw.split(";")) {
    const eq = part.indexOf("=");
    if (eq === -1) continue;
    if (part.slice(0, eq).trim() === name) return part.slice(eq + 1).trim();
  }
  return "";
}

// Express middleware. No-op when auth is not configured. On success it sets an
// auth cookie so the (header-less) browser WebSocket handshake can authenticate.
export function basicAuth({ user, password }) {
  if (!user || !password) return (_req, _res, next) => next();
  const token = authToken(user, password);
  return (req, res, next) => {
    if (check(req.headers.authorization, user, password)) {
      res.setHeader("Set-Cookie", `mcconsole=${token}; HttpOnly; SameSite=Strict; Path=/`);
      return next();
    }
    res.set("WWW-Authenticate", 'Basic realm="minecrafft-console"');
    res.status(401).send("Authentication required.");
  };
}

// Validate a WebSocket upgrade: accept either the Authorization header (API
// clients) or the auth cookie set after a Basic-Auth page load (browsers).
export function wsAuthorized(req, { user, password }) {
  if (!user || !password) return true;
  if (check(req.headers.authorization, user, password)) return true;
  const token = authToken(user, password);
  const cookie = cookieValue(req, "mcconsole");
  return cookie.length === token.length && safeEqual(cookie, token);
}
