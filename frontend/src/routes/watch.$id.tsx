import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AppHeader } from "@/components/AppHeader";
import { SnakeBoard } from "@/components/SnakeBoard";
import { getApi } from "@/services/api";
import type { ActiveGame } from "@/services/types";

export const Route = createFileRoute("/watch/$id")({
  head: () => ({ meta: [{ title: "Spectate — Snake Arena" }] }),
  component: Spectate,
});

function Spectate() {
  const { id } = Route.useParams();
  const [game, setGame] = useState<ActiveGame | null>(null);
  useEffect(() => getApi().subscribeActiveGame(id, setGame), [id]);

  return (
    <div className="min-h-screen flex flex-col">
      <AppHeader />
      <main className="flex-1 mx-auto max-w-5xl w-full px-4 py-8">
        <Link to="/watch" className="text-sm text-muted-foreground hover:text-foreground">
          ← All live games
        </Link>
        {!game ? (
          <div className="mt-10 rounded-xl border border-dashed border-border p-10 text-center">
            <p className="text-muted-foreground">This game ended or doesn't exist.</p>
          </div>
        ) : (
          <div className="mt-6 grid lg:grid-cols-[auto_1fr] gap-8 items-start">
            <SnakeBoard
              state={game}
              size={480}
              className="rounded-xl border border-border shadow-lg"
            />
            <aside className="w-full max-w-sm space-y-4">
              <div className="rounded-xl border border-border bg-card p-5">
                <h2 className="text-xl font-bold">@{game.username}</h2>
                <p className="text-sm text-muted-foreground capitalize">{game.mode} mode</p>
              </div>
              <div className="rounded-xl border border-border bg-card p-5">
                <div className="flex items-baseline justify-between">
                  <span className="text-muted-foreground">Score</span>
                  <span className="text-4xl font-black tabular-nums">{game.score}</span>
                </div>
                <div className="mt-3 flex items-center gap-2 text-sm">
                  <span
                    className={`size-2 rounded-full ${game.alive ? "bg-emerald-500 animate-pulse" : "bg-rose-500"}`}
                  />
                  {game.alive ? "Live" : "Game over"}
                </div>
              </div>
            </aside>
          </div>
        )}
      </main>
    </div>
  );
}
