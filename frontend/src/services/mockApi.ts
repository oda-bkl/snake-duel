import type { ApiService } from "./api";
import type { ActiveGame, AuthSession, GameMode, ScoreEntry, User } from "./types";

const STORAGE_KEY = "snake.mock.v1";
const SESSION_KEY = "snake.mock.session.v1";

interface MockDB {
  users: Array<{ id: string; username: string; password: string }>;
  scores: ScoreEntry[];
}

function loadDB(): MockDB {
  if (typeof localStorage === "undefined") return { users: [], scores: [] };
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return seedDB();
    return JSON.parse(raw) as MockDB;
  } catch {
    return seedDB();
  }
}

function seedDB(): MockDB {
  const db: MockDB = {
    users: [
      { id: "u_demo", username: "demo", password: "demo" },
      { id: "u_alice", username: "alice", password: "alice" },
    ],
    scores: [
      {
        id: "s1",
        userId: "u_demo",
        username: "demo",
        mode: "walls",
        score: 42,
        createdAt: Date.now() - 100000,
      },
      {
        id: "s2",
        userId: "u_alice",
        username: "alice",
        mode: "walls",
        score: 31,
        createdAt: Date.now() - 80000,
      },
      {
        id: "s3",
        userId: "u_demo",
        username: "demo",
        mode: "wrap",
        score: 88,
        createdAt: Date.now() - 50000,
      },
      {
        id: "s4",
        userId: "u_alice",
        username: "alice",
        mode: "wrap",
        score: 64,
        createdAt: Date.now() - 30000,
      },
    ],
  };
  saveDB(db);
  return db;
}

function saveDB(db: MockDB) {
  if (typeof localStorage === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(db));
}

function loadSession(): AuthSession | null {
  if (typeof localStorage === "undefined") return null;
  const raw = localStorage.getItem(SESSION_KEY);
  return raw ? (JSON.parse(raw) as AuthSession) : null;
}

function saveSession(s: AuthSession | null) {
  if (typeof localStorage === "undefined") return;
  if (s) localStorage.setItem(SESSION_KEY, JSON.stringify(s));
  else localStorage.removeItem(SESSION_KEY);
}

function uid(prefix = "id") {
  return `${prefix}_${Math.random().toString(36).slice(2, 10)}`;
}

// In-memory active games and pub/sub (volatile, ideal for "watch live")
const activeGames = new Map<string, ActiveGame>();
const gameSubs = new Map<string, Set<(g: ActiveGame | null) => void>>();
const listSubs = new Set<(g: ActiveGame[]) => void>();

function notifyGame(id: string) {
  const subs = gameSubs.get(id);
  if (subs) subs.forEach((cb) => cb(activeGames.get(id) ?? null));
  notifyList();
}
function notifyList() {
  const arr = Array.from(activeGames.values()).sort((a, b) => b.updatedAt - a.updatedAt);
  listSubs.forEach((cb) => cb(arr));
}

export const mockApi: ApiService = {
  async signup(username, password) {
    const db = loadDB();
    if (!username.trim() || !password) throw new Error("Username and password required");
    if (db.users.some((u) => u.username.toLowerCase() === username.toLowerCase())) {
      throw new Error("Username already taken");
    }
    const user = { id: uid("u"), username: username.trim(), password };
    db.users.push(user);
    saveDB(db);
    const session: AuthSession = {
      user: { id: user.id, username: user.username },
      token: uid("t"),
    };
    saveSession(session);
    return session;
  },

  async login(username, password) {
    const db = loadDB();
    const u = db.users.find(
      (x) => x.username.toLowerCase() === username.toLowerCase() && x.password === password,
    );
    if (!u) throw new Error("Invalid credentials");
    const session: AuthSession = { user: { id: u.id, username: u.username }, token: uid("t") };
    saveSession(session);
    return session;
  },

  async logout() {
    saveSession(null);
  },

  async currentSession() {
    return loadSession();
  },

  async submitScore({ mode, score }) {
    const session = loadSession();
    if (!session) throw new Error("Not authenticated");
    const db = loadDB();
    const entry: ScoreEntry = {
      id: uid("s"),
      userId: session.user.id,
      username: session.user.username,
      mode,
      score,
      createdAt: Date.now(),
    };
    db.scores.push(entry);
    saveDB(db);
    return entry;
  },

  async getLeaderboard(mode, limit = 10) {
    const db = loadDB();
    return db.scores
      .filter((s) => s.mode === mode)
      .sort((a, b) => b.score - a.score || a.createdAt - b.createdAt)
      .slice(0, limit);
  },

  async upsertActiveGame(game) {
    const session = loadSession();
    const username = session?.user.username ?? "guest";
    const id = game.id ?? uid("g");
    const full: ActiveGame = { ...game, id, username, updatedAt: Date.now() };
    activeGames.set(full.id, full);
    notifyGame(full.id);
    return full;
  },

  async endActiveGame(id) {
    const g = activeGames.get(id);
    if (g) {
      activeGames.set(id, { ...g, alive: false, updatedAt: Date.now() });
      notifyGame(id);
      // Remove shortly after so spectators see "game over" briefly
      setTimeout(() => {
        activeGames.delete(id);
        notifyGame(id);
      }, 4000);
    }
  },

  async listActiveGames() {
    return Array.from(activeGames.values()).sort((a, b) => b.updatedAt - a.updatedAt);
  },

  async getActiveGame(id) {
    return activeGames.get(id) ?? null;
  },

  subscribeActiveGame(id, cb) {
    if (!gameSubs.has(id)) gameSubs.set(id, new Set());
    gameSubs.get(id)!.add(cb);
    cb(activeGames.get(id) ?? null);
    return () => {
      gameSubs.get(id)?.delete(cb);
    };
  },

  subscribeActiveGames(cb) {
    listSubs.add(cb);
    cb(Array.from(activeGames.values()).sort((a, b) => b.updatedAt - a.updatedAt));
    return () => {
      listSubs.delete(cb);
    };
  },
};

// Test helpers
export function __resetMock() {
  if (typeof localStorage !== "undefined") {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(SESSION_KEY);
  }
  activeGames.clear();
  gameSubs.clear();
  listSubs.clear();
}
