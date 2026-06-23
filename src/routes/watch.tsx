import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AppHeader } from "@/components/AppHeader";
import { getApi } from "@/services/api";
import type { ActiveGame } from "@/services/types";

export const Route = createFileRoute("/watch")({
  head: () => ({ meta: [{ title: "Watch live — Snake Arena" }] }),
  component: Watch,
});

function Watch() {
  const [games, setGames] = useState<ActiveGame[]>([]);
  useEffect(() => getApi().subscribeActiveGames(setGames), []);

  return (
    <div className="min-h-screen flex flex-col">
      <AppHeader />
      <main className="flex-1 mx-auto max-w-3xl w-full px-4 py-10">
        <h1 className="text-3xl font-black tracking-tight">Watch live</h1>
        <p className="text-muted-foreground mt-1">Active games right now.</p>

        {games.length === 0 ? (
          <div className="mt-10 rounded-xl border border-dashed border-border p-10 text-center">
            <p className="text-muted-foreground">No live games. <Link to="/play" className="underline text-foreground">Start one</Link>.</p>
          </div>
        ) : (
          <ul className="mt-6 grid sm:grid-cols-2 gap-3">
            {games.map((g) => (
              <li key={g.id}>
                <Link
                  to="/watch/$id"
                  params={{ id: g.id }}
                  className="block p-4 rounded-xl border border-border bg-card hover:bg-accent transition"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">@{g.username}</span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-accent text-accent-foreground capitalize">{g.mode}</span>
                  </div>
                  <div className="mt-2 flex items-baseline justify-between">
                    <span className="text-sm text-muted-foreground">Score</span>
                    <span className="font-black text-2xl tabular-nums">{g.score}</span>
                  </div>
                  <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                    <span className={`size-2 rounded-full ${g.alive ? "bg-emerald-500 animate-pulse" : "bg-rose-500"}`} />
                    {g.alive ? "Live" : "Ended"}
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}
