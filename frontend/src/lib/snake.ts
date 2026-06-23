import type { GameMode } from "@/services/types";

export type Dir = "up" | "down" | "left" | "right";
export interface Point {
  x: number;
  y: number;
}

export interface GameState {
  snake: Point[]; // head at [0]
  dir: Dir;
  pendingDir: Dir;
  food: Point;
  gridSize: number;
  mode: GameMode;
  alive: boolean;
  score: number;
}

const DIRS: Record<Dir, Point> = {
  up: { x: 0, y: -1 },
  down: { x: 0, y: 1 },
  left: { x: -1, y: 0 },
  right: { x: 1, y: 0 },
};

const OPPOSITE: Record<Dir, Dir> = { up: "down", down: "up", left: "right", right: "left" };

export function createGame(mode: GameMode, gridSize = 20): GameState {
  const mid = Math.floor(gridSize / 2);
  const snake: Point[] = [
    { x: mid, y: mid },
    { x: mid - 1, y: mid },
    { x: mid - 2, y: mid },
  ];
  return {
    snake,
    dir: "right",
    pendingDir: "right",
    food: spawnFood(snake, gridSize),
    gridSize,
    mode,
    alive: true,
    score: 0,
  };
}

export function spawnFood(
  snake: Point[],
  gridSize: number,
  rng: () => number = Math.random,
): Point {
  const occupied = new Set(snake.map((p) => `${p.x},${p.y}`));
  const free: Point[] = [];
  for (let x = 0; x < gridSize; x++) {
    for (let y = 0; y < gridSize; y++) {
      if (!occupied.has(`${x},${y}`)) free.push({ x, y });
    }
  }
  if (free.length === 0) return { x: 0, y: 0 };
  return free[Math.floor(rng() * free.length)];
}

export function setDirection(state: GameState, dir: Dir): GameState {
  // prevent 180° reversal
  if (OPPOSITE[state.dir] === dir) return state;
  return { ...state, pendingDir: dir };
}

export function tick(state: GameState, rng: () => number = Math.random): GameState {
  if (!state.alive) return state;
  const dir = state.pendingDir;
  const delta = DIRS[dir];
  const head = state.snake[0];
  let nx = head.x + delta.x;
  let ny = head.y + delta.y;

  if (state.mode === "wrap") {
    nx = (nx + state.gridSize) % state.gridSize;
    ny = (ny + state.gridSize) % state.gridSize;
  } else if (nx < 0 || ny < 0 || nx >= state.gridSize || ny >= state.gridSize) {
    return { ...state, alive: false, dir };
  }

  const newHead: Point = { x: nx, y: ny };
  const eating = newHead.x === state.food.x && newHead.y === state.food.y;
  const newBody = eating ? state.snake : state.snake.slice(0, -1);

  // self-collision (compare against newBody since tail moves away when not eating)
  if (newBody.some((p) => p.x === newHead.x && p.y === newHead.y)) {
    return { ...state, alive: false, dir };
  }

  const snake = [newHead, ...newBody];
  return {
    ...state,
    snake,
    dir,
    score: state.score + (eating ? 1 : 0),
    food: eating ? spawnFood(snake, state.gridSize, rng) : state.food,
    alive: true,
  };
}
