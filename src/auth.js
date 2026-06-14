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

// Express middleware. No-op when auth is not configured.
export function basicAuth({ user, password }) {
  if (!user || !password) return (_req, _res, next) => next();
  return (req, res, next) => {
    if (check(req.headers.authorization, user, password)) return next();
    res.set("WWW-Authenticate", 'Basic realm="minecrafft-console"');
    res.status(401).send("Authentication required.");
  };
}

// Validate an incoming WebSocket upgrade request the same way.
export function wsAuthorized(req, { user, password }) {
  if (!user || !password) return true;
  return check(req.headers.authorization, user, password);
}
