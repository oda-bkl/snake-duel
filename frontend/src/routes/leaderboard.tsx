import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AppHeader } from "@/components/AppHeader";
import { getApi } from "@/services/api";
import type { GameMode, ScoreEntry } from "@/services/types";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export const Route = createFileRoute("/leaderboard")({
  head: () => ({ meta: [{ title: "Leaderboard — Snake Arena" }] }),
  component: Leaderboard,
});

function Leaderboard() {
  return (
    <div className="min-h-screen flex flex-col">
      <AppHeader />
      <main className="flex-1 mx-auto max-w-3xl w-full px-4 py-10">
        <h1 className="text-3xl font-black tracking-tight">Leaderboard</h1>
        <p className="text-muted-foreground mt-1">Top 10 scores per mode.</p>
        <Tabs defaultValue="walls" className="mt-6">
          <TabsList>
            <TabsTrigger value="walls">Walls</TabsTrigger>
            <TabsTrigger value="wrap">Wrap</TabsTrigger>
          </TabsList>
          <TabsContent value="walls">
            <Board mode="walls" />
          </TabsContent>
          <TabsContent value="wrap">
            <Board mode="wrap" />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

function Board({ mode }: { mode: GameMode }) {
  const [rows, setRows] = useState<ScoreEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    setRows(null);
    setError(null);
    getApi()
      .getLeaderboard(mode, 10)
      .then((r) => {
        if (!cancelled) setRows(r);
      })
      .catch((e) => {
        if (!cancelled) setError((e as Error).message);
      });
    return () => {
      cancelled = true;
    };
  }, [mode]);

  if (error) return <p className="mt-6 text-destructive">{error}</p>;
  if (!rows) return <p className="mt-6 text-muted-foreground">Loading…</p>;
  if (rows.length === 0)
    return <p className="mt-6 text-muted-foreground">No scores yet. Be the first!</p>;

  return (
    <ol className="mt-4 rounded-xl border border-border bg-card divide-y divide-border overflow-hidden">
      {rows.map((r, i) => (
        <li key={r.id} className="flex items-center gap-4 px-4 py-3">
          <span
            className={`w-8 text-center font-black ${i < 3 ? "text-primary" : "text-muted-foreground"}`}
          >
            #{i + 1}
          </span>
          <span className="flex-1 font-medium">{r.username}</span>
          <span className="text-xs text-muted-foreground hidden sm:inline">
            {new Date(r.createdAt).toLocaleDateString()}
          </span>
          <span className="font-black tabular-nums text-lg">{r.score}</span>
        </li>
      ))}
    </ol>
  );
}
