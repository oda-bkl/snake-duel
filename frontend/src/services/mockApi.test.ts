import { describe, it, expect, beforeEach } from "vitest";
import { mockApi, __resetMock } from "@/services/mockApi";

beforeEach(() => __resetMock());

describe("mockApi auth", () => {
  it("signs up a new user and persists session", async () => {
    const s = await mockApi.signup("zoe", "pw");
    expect(s.user.username).toBe("zoe");
    const cur = await mockApi.currentSession();
    expect(cur?.user.id).toBe(s.user.id);
  });

  it("rejects duplicate signup", async () => {
    await mockApi.signup("zoe", "pw");
    await expect(mockApi.signup("zoe", "pw")).rejects.toThrow(/taken/i);
  });

  it("logs in seed user demo/demo", async () => {
    const s = await mockApi.login("demo", "demo");
    expect(s.user.username).toBe("demo");
  });

  it("rejects bad credentials", async () => {
    await expect(mockApi.login("demo", "wrong")).rejects.toThrow(/invalid/i);
  });

  it("logout clears session", async () => {
    await mockApi.login("demo", "demo");
    await mockApi.logout();
    expect(await mockApi.currentSession()).toBeNull();
  });
});

describe("mockApi scores", () => {
  it("requires auth to submit a score", async () => {
    await expect(mockApi.submitScore({ mode: "walls", score: 10 })).rejects.toThrow(/auth/i);
  });

  it("submits scores and sorts the leaderboard descending", async () => {
    await mockApi.login("demo", "demo");
    await mockApi.submitScore({ mode: "walls", score: 5 });
    await mockApi.submitScore({ mode: "walls", score: 99 });
    const top = await mockApi.getLeaderboard("walls", 10);
    expect(top[0].score).toBe(99);
    expect(top.every((r) => r.mode === "walls")).toBe(true);
  });
});

describe("mockApi active games", () => {
  it("publishes and lists active games, then ends them", async () => {
    await mockApi.login("demo", "demo");
    const g = await mockApi.upsertActiveGame({
      id: "g1",
      userId: "u_demo",
      mode: "wrap",
      score: 0,
      snake: [{ x: 0, y: 0 }],
      food: { x: 1, y: 1 },
      gridSize: 10,
      alive: true,
    });
    expect(g.username).toBe("demo");
    const list = await mockApi.listActiveGames();
    expect(list.map((x) => x.id)).toContain("g1");
    await mockApi.endActiveGame("g1");
    const after = await mockApi.getActiveGame("g1");
    expect(after?.alive).toBe(false);
  });

  it("notifies subscribers on update", async () => {
    await mockApi.login("demo", "demo");
    const received: Array<number> = [];
    const unsub = mockApi.subscribeActiveGames((list) => received.push(list.length));
    await mockApi.upsertActiveGame({
      id: "g2",
      userId: "u_demo",
      mode: "walls",
      score: 0,
      snake: [{ x: 0, y: 0 }],
      food: { x: 1, y: 1 },
      gridSize: 10,
      alive: true,
    });
    unsub();
    expect(received.at(-1)).toBe(1);
  });
});
