import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useCallback, useEffect, useRef, useState } from "react";
import { AppHeader } from "@/components/AppHeader";
import { SnakeBoard } from "@/components/SnakeBoard";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { createGame, setDirection, tick, type Dir, type GameState } from "@/lib/snake";
import { getApi } from "@/services/api";
import type { GameMode } from "@/services/types";
import { toast } from "sonner";

export const Route = createFileRoute("/play")({
  head: () => ({ meta: [{ title: "Play — Snake Arena" }] }),
  component: Play,
});

const TICK_MS = 110;

function Play() {
  const { user } = useAuth();
  const nav = useNavigate();
  const [mode, setMode] = useState<GameMode>("walls");
  const [state, setState] = useState<GameState>(() => createGame("walls"));
  const [running, setRunning] = useState(false);
  const gameIdRef = useRef<string | null>(null);
  const runningRef = useRef(running);
  runningRef.current = running;
  const userRef = useRef(user);
  userRef.current = user;

  const reset = useCallback((m: GameMode) => {
    setMode(m);
    setState(createGame(m));
    setRunning(false);
    gameIdRef.current = null;
  }, []);

  // Keyboard
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const map: Record<string, Dir> = {
        ArrowUp: "up", ArrowDown: "down", ArrowLeft: "left", ArrowRight: "right",
        w: "up", s: "down", a: "left", d: "right", W: "up", S: "down", A: "left", D: "right",
      };
      const d = map[e.key];
      if (d) {
        e.preventDefault();
        setState((s) => setDirection(s, d));
        if (!running && state.alive) setRunning(true);
      } else if (e.key === " ") {
        e.preventDefault();
        setRunning((r) => !r);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [running, state.alive]);

  // Game loop
  useEffect(() => {
    if (!running || !state.alive) return;
    const id = setInterval(() => {
      setState((s) => tick(s));
    }, TICK_MS);
    return () => clearInterval(id);
  }, [running, state.alive]);

  // Publish active game for spectators; store server-returned id for subsequent updates
  useEffect(() => {
    if (!running) return;
    const api = getApi();
    api.upsertActiveGame({
      id: gameIdRef.current ?? undefined,
      userId: user?.id ?? "guest",
      mode: state.mode,
      score: state.score,
      snake: state.snake,
      food: state.food,
      gridSize: state.gridSize,
      alive: state.alive,
    }).then((g) => { gameIdRef.current = g.id; }).catch(() => {});
  }, [state, running, user]);

  // Handle death: submit score, end active game
  useEffect(() => {
    if (state.alive) return;
    const api = getApi();
    if (gameIdRef.current) api.endActiveGame(gameIdRef.current);
    if (runningRef.current && userRef.current && state.score > 0) {
      api.submitScore({ mode: state.mode, score: state.score })
        .then(() => toast.success(`Score saved: ${state.score}`))
        .catch((e) => toast.error((e as Error).message));
    }
    setRunning(false);
  }, [state.alive, state.score, state.mode]);

  return (
    <div className="min-h-screen flex flex-col">
      <AppHeader />
      <main className="flex-1 mx-auto max-w-5xl w-full px-4 py-8 grid lg:grid-cols-[auto_1fr] gap-8 items-start">
        <div className="flex flex-col items-center gap-3">
          <SnakeBoard state={state} size={480} className="rounded-xl shadow-lg border border-border" />
          <p className="text-xs text-muted-foreground">Arrow keys / WASD · Space = pause</p>
        </div>
        <aside className="w-full max-w-sm space-y-6">
          <div className="rounded-xl border border-border bg-card p-5">
            <div className="flex items-baseline justify-between">
              <h2 className="font-semibold text-lg">Score</h2>
              <span className="text-4xl font-black tabular-nums">{state.score}</span>
            </div>
            <div className="mt-1 text-sm text-muted-foreground">Mode: <span className="font-medium text-foreground capitalize">{state.mode}</span></div>
          </div>

          <div className="rounded-xl border border-border bg-card p-5 space-y-3">
            <h2 className="font-semibold">Mode</h2>
            <div className="grid grid-cols-2 gap-2">
              <Button variant={mode === "walls" ? "default" : "outline"} onClick={() => reset("walls")}>Walls</Button>
              <Button variant={mode === "wrap" ? "default" : "outline"} onClick={() => reset("wrap")}>Wrap</Button>
            </div>
            <div className="flex gap-2">
              {state.alive ? (
                <Button className="flex-1" onClick={() => setRunning((r) => !r)}>
                  {running ? "Pause" : "Start"}
                </Button>
              ) : (
                <Button className="flex-1" onClick={() => reset(mode)}>Play again</Button>
              )}
              <Button variant="outline" onClick={() => reset(mode)}>Reset</Button>
            </div>
          </div>

          {!user && (
            <div className="rounded-xl border border-dashed border-border bg-card/50 p-5 text-sm">
              <p className="text-muted-foreground">
                You're playing as a guest. <button onClick={() => nav({ to: "/auth" })} className="underline text-foreground">Sign in</button> to save scores.
              </p>
            </div>
          )}
        </aside>
      </main>
    </div>
  );
}
