import crypto from "node:crypto";

// In-memory session store (cleared on restart -> users re-login).
const sessions = new Set();

function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  const ab = Buffer.from(a);
  const bb = Buffer.from(b);
  if (ab.length !== bb.length) return false;
  return crypto.timingSafeEqual(ab, bb);
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

export function authConfigured({ user, password }) {
  return Boolean(user && password);
}

export function verifyCredentials(user, password, creds) {
  return safeEqual(user, creds.user) && safeEqual(password, creds.password);
}

export function createSession() {
  const token = crypto.randomBytes(24).toString("hex");
  sessions.add(token);
  return token;
}

export function sessionTokenFromReq(req) {
  return cookieValue(req, "mcsession");
}

export function destroySession(token) {
  if (token) sessions.delete(token);
}

const COOKIE_BASE = "mcsession=%; HttpOnly; SameSite=Strict; Path=/";
export const sessionCookieHeader = (token) => COOKIE_BASE.replace("%", token) + "; Max-Age=604800";
export const clearCookieHeader = () => COOKIE_BASE.replace("%", "") + "; Max-Age=0";

function isAuthed(req) {
  const token = sessionTokenFromReq(req);
  return Boolean(token) && sessions.has(token);
}

// Paths reachable without a session (the login page + the login endpoint).
const PUBLIC_PATHS = new Set(["/login.html", "/login.css", "/api/login"]);

// Express middleware. No-op when auth isn't configured. Unauthenticated API
// calls get 401; unauthenticated page loads are redirected to the login page.
export function authGate(creds) {
  if (!authConfigured(creds)) return (_req, _res, next) => next();
  return (req, res, next) => {
    if (PUBLIC_PATHS.has(req.path) || isAuthed(req)) return next();
    if (req.path.startsWith("/api/")) return res.status(401).json({ error: "not authenticated" });
    return res.redirect("/login.html");
  };
}

// WebSocket upgrade auth: session cookie only (browsers send it on the handshake).
export function wsAuthorized(req, creds) {
  if (!authConfigured(creds)) return true;
  return isAuthed(req);
}
