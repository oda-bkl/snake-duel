export type GameMode = "walls" | "wrap";

export interface User {
  id: string;
  username: string;
}

export interface AuthSession {
  user: User;
  token: string;
}

export interface ScoreEntry {
  id: string;
  userId: string;
  username: string;
  mode: GameMode;
  score: number;
  createdAt: number;
}

export interface ActiveGame {
  id: string;
  userId: string;
  username: string;
  mode: GameMode;
  score: number;
  snake: Array<{ x: number; y: number }>;
  food: { x: number; y: number };
  gridSize: number;
  alive: boolean;
  updatedAt: number;
}
