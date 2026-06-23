import type { ActiveGame, AuthSession, GameMode, ScoreEntry } from "./types";

export interface ApiService {
  // Auth
  signup(username: string, password: string): Promise<AuthSession>;
  login(username: string, password: string): Promise<AuthSession>;
  logout(): Promise<void>;
  currentSession(): Promise<AuthSession | null>;

  // Scores
  submitScore(input: { mode: GameMode; score: number }): Promise<ScoreEntry>;
  getLeaderboard(mode: GameMode, limit?: number): Promise<ScoreEntry[]>;

  // Active games (for spectating)
  // id is optional: omit on first call and use the server-returned id for updates
  upsertActiveGame(
    game: Omit<ActiveGame, "id" | "username" | "updatedAt"> & { id?: string },
  ): Promise<ActiveGame>;
  endActiveGame(id: string): Promise<void>;
  listActiveGames(): Promise<ActiveGame[]>;
  getActiveGame(id: string): Promise<ActiveGame | null>;
  // subscribe* uses callbacks; real backend implements via polling or SSE (not OpenAPI)
  subscribeActiveGame(id: string, cb: (game: ActiveGame | null) => void): () => void;
  subscribeActiveGames(cb: (games: ActiveGame[]) => void): () => void;
}

import { mockApi } from "./mockApi";

let _api: ApiService = mockApi;
let _token: string | null = null;

export function getApi(): ApiService {
  return _api;
}

export function setApi(api: ApiService) {
  _api = api;
}

export function getAuthToken(): string | null {
  return _token;
}

export function setAuthToken(token: string | null) {
  _token = token;
}
