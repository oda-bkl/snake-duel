import { useEffect, useRef } from "react";
import type { GameState } from "@/lib/snake";

interface Props {
  state: Pick<GameState, "snake" | "food" | "gridSize" | "alive">;
  size?: number;
  className?: string;
}

export function SnakeBoard({ state, size = 480, className }: Props) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const cell = size / state.gridSize;
    const css = getComputedStyle(canvas);
    const bg = css.getPropertyValue("--game-board").trim() || "#0f172a";
    const fg = css.getPropertyValue("--game-snake").trim() || "#22d3ee";
    const head = css.getPropertyValue("--game-snake-head").trim() || "#67e8f9";
    const food = css.getPropertyValue("--game-food").trim() || "#f43f5e";

    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, size, size);

    // grid lines (subtle)
    ctx.strokeStyle = "rgba(255,255,255,0.04)";
    for (let i = 1; i < state.gridSize; i++) {
      ctx.beginPath();
      ctx.moveTo(i * cell, 0);
      ctx.lineTo(i * cell, size);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, i * cell);
      ctx.lineTo(size, i * cell);
      ctx.stroke();
    }

    // food
    ctx.fillStyle = food;
    const fpad = cell * 0.15;
    ctx.beginPath();
    ctx.arc(
      state.food.x * cell + cell / 2,
      state.food.y * cell + cell / 2,
      cell / 2 - fpad,
      0,
      Math.PI * 2,
    );
    ctx.fill();

    // snake
    state.snake.forEach((p, i) => {
      ctx.fillStyle = i === 0 ? head : fg;
      const pad = cell * 0.08;
      ctx.fillRect(p.x * cell + pad, p.y * cell + pad, cell - pad * 2, cell - pad * 2);
    });

    if (!state.alive) {
      ctx.fillStyle = "rgba(0,0,0,0.6)";
      ctx.fillRect(0, 0, size, size);
      ctx.fillStyle = "#fff";
      ctx.font = `bold ${Math.floor(size / 12)}px ui-sans-serif, system-ui`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("Game Over", size / 2, size / 2);
    }
  }, [state, size]);

  return <canvas ref={ref} width={size} height={size} className={className} />;
}
