import type { ActiveGame, AuthSession, GameMode, ScoreEntry, User } from "./types";

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
  upsertActiveGame(game: Omit<ActiveGame, "username" | "updatedAt">): Promise<ActiveGame>;
  endActiveGame(id: string): Promise<void>;
  listActiveGames(): Promise<ActiveGame[]>;
  getActiveGame(id: string): Promise<ActiveGame | null>;
  subscribeActiveGame(id: string, cb: (game: ActiveGame | null) => void): () => void;
  subscribeActiveGames(cb: (games: ActiveGame[]) => void): () => void;
}

import { httpApi } from "./httpApi";

let _api: ApiService = httpApi;

export function getApi(): ApiService {
  return _api;
}

export function setApi(api: ApiService) {
  _api = api;
}
