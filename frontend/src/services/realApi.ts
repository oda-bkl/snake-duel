import type { ApiService } from "./api";
import type { ActiveGame, AuthSession, GameMode, ScoreEntry } from "./types";
import { apiFetch } from "./httpClient";

const POLL_MS = 2000;

export const realApi: ApiService = {
  async signup(username, password) {
    return apiFetch<AuthSession>("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
  },

  async login(username, password) {
    return apiFetch<AuthSession>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
  },

  async logout() {
    await apiFetch("/api/auth/logout", { method: "POST" });
  },

  async currentSession() {
    return apiFetch<AuthSession | null>("/api/auth/session");
  },

  async submitScore(input) {
    return apiFetch<ScoreEntry>("/api/scores", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  async getLeaderboard(mode: GameMode, limit = 10) {
    return apiFetch<ScoreEntry[]>(`/api/scores/leaderboard?mode=${mode}&limit=${limit}`);
  },

  async upsertActiveGame(game) {
    return apiFetch<ActiveGame>("/api/games/active", {
      method: "POST",
      body: JSON.stringify(game),
    });
  },

  async endActiveGame(id) {
    await apiFetch(`/api/games/active/${id}/end`, { method: "POST" });
  },

  async listActiveGames() {
    return apiFetch<ActiveGame[]>("/api/games/active");
  },

  async getActiveGame(id) {
    return apiFetch<ActiveGame | null>(`/api/games/active/${id}`);
  },

  subscribeActiveGame(id, cb) {
    let cancelled = false;
    const poll = async () => {
      while (!cancelled) {
        try {
          const g = await realApi.getActiveGame(id);
          if (!cancelled) cb(g);
          if (!g || !g.alive) break;
        } catch {
          // network error — keep polling
        }
        await new Promise((r) => setTimeout(r, POLL_MS));
      }
    };
    poll();
    return () => {
      cancelled = true;
    };
  },

  subscribeActiveGames(cb) {
    let cancelled = false;
    const poll = async () => {
      while (!cancelled) {
        try {
          const games = await realApi.listActiveGames();
          if (!cancelled) cb(games);
        } catch {
          // network error — keep polling
        }
        await new Promise((r) => setTimeout(r, POLL_MS));
      }
    };
    poll();
    return () => {
      cancelled = true;
    };
  },
};
