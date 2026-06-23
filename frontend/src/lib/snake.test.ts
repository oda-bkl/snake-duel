import { describe, it, expect } from "vitest";
import { createGame, tick, setDirection, spawnFood } from "@/lib/snake";

describe("snake game logic", () => {
  it("creates a game with snake in the middle, length 3, alive", () => {
    const g = createGame("walls", 20);
    expect(g.snake.length).toBe(3);
    expect(g.alive).toBe(true);
    expect(g.score).toBe(0);
  });

  it("advances the snake on tick", () => {
    const g = createGame("walls", 20);
    const next = tick(g);
    expect(next.snake[0].x).toBe(g.snake[0].x + 1);
    expect(next.snake.length).toBe(3);
  });

  it("prevents 180° reversal via setDirection", () => {
    const g = createGame("walls", 20); // moving right
    const g2 = setDirection(g, "left");
    expect(g2.pendingDir).toBe("right");
  });

  it("kills the snake on wall in walls mode", () => {
    let g = createGame("walls", 5); // mid=2, head at (2,2)
    for (let i = 0; i < 10 && g.alive; i++) g = tick(g);
    expect(g.alive).toBe(false);
  });

  it("wraps around in wrap mode", () => {
    let g = createGame("wrap", 5);
    for (let i = 0; i < 10; i++) g = tick(g);
    expect(g.alive).toBe(true);
  });

  it("eats food, grows, and increments score", () => {
    const g = createGame("walls", 20);
    const headNext = { x: g.snake[0].x + 1, y: g.snake[0].y };
    const placed = { ...g, food: headNext };
    const next = tick(placed);
    expect(next.score).toBe(1);
    expect(next.snake.length).toBe(4);
  });

  it("detects self-collision", () => {
    // Build a state where moving forward hits own body
    const g = createGame("walls", 20);
    // Force a U-turn-prone shape: snake of length 5 in an L; then move into self
    const snake = [
      { x: 5, y: 5 }, { x: 5, y: 6 }, { x: 6, y: 6 }, { x: 6, y: 5 }, { x: 7, y: 5 },
    ];
    const s = { ...g, snake, dir: "up" as const, pendingDir: "up" as const, food: { x: 0, y: 0 } };
    // moving up from (5,5) — new head (5,4); not self. Try left from snake[0] going down:
    const s2 = setDirection(s, "left");
    // moving left: (4,5) not self either. Use a clearer case: tail bites head when shrinking
    const tight = {
      ...g,
      snake: [
        { x: 5, y: 5 }, { x: 4, y: 5 }, { x: 4, y: 6 }, { x: 5, y: 6 }, { x: 5, y: 7 },
      ],
      dir: "down" as const,
      pendingDir: "down" as const,
      food: { x: 0, y: 0 },
    };
    const next = tick(tight);
    expect(next.alive).toBe(false);
    expect(s2).toBeDefined();
  });

  it("spawnFood never lands on the snake", () => {
    const snake = [{ x: 0, y: 0 }, { x: 0, y: 1 }];
    const f = spawnFood(snake, 5, () => 0.5);
    expect(snake.find((p) => p.x === f.x && p.y === f.y)).toBeUndefined();
  });
});
