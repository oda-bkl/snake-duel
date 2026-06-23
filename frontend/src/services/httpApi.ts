import type { ApiService } from "./api";
import type { ActiveGame, AuthSession, GameMode, ScoreEntry } from "./types";

const TOKEN_KEY = "snake.token.v1";
const BASE = "/api";

function getToken(): string | null {
  return typeof localStorage !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null;
}

function saveToken(token: string | null) {
  if (typeof localStorage === "undefined") return;
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(init.headers as Record<string, string> | undefined),
    },
  });
  if (res.status === 204) return undefined as T;
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    const msg = body?.detail ?? body?.message ?? res.statusText;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return body as T;
}

export const httpApi: ApiService = {
  async signup(username, password) {
    const session = await request<AuthSession>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    saveToken(session.token);
    return session;
  },

  async login(username, password) {
    const session = await request<AuthSession>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    saveToken(session.token);
    return session;
  },

  async logout() {
    await request<void>("/auth/logout", { method: "POST" });
    saveToken(null);
  },

  async currentSession() {
    if (!getToken()) return null;
    return request<AuthSession | null>("/auth/session");
  },

  async submitScore({ mode, score }) {
    return request<ScoreEntry>("/scores", {
      method: "POST",
      body: JSON.stringify({ mode, score }),
    });
  },

  async getLeaderboard(mode, limit = 10) {
    return request<ScoreEntry[]>(`/leaderboard?mode=${mode}&limit=${limit}`);
  },

  async upsertActiveGame(game) {
    return request<ActiveGame>(`/games/${game.id}`, {
      method: "PUT",
      body: JSON.stringify(game),
    });
  },

  async endActiveGame(id) {
    await request<void>(`/games/${id}`, { method: "DELETE" });
  },

  async listActiveGames() {
    return request<ActiveGame[]>("/games");
  },

  async getActiveGame(id) {
    return request<ActiveGame | null>(`/games/${id}`);
  },

  subscribeActiveGame(id, cb) {
    const es = new EventSource(`${BASE}/games/${id}/stream`);
    es.onmessage = (e) => cb(JSON.parse(e.data) as ActiveGame | null);
    return () => es.close();
  },

  subscribeActiveGames(cb) {
    const es = new EventSource(`${BASE}/games/stream`);
    es.onmessage = (e) => cb(JSON.parse(e.data) as ActiveGame[]);
    return () => es.close();
  },
};
