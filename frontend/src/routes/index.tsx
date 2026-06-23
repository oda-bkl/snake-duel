import { createFileRoute, Link } from "@tanstack/react-router";
import { AppHeader } from "@/components/AppHeader";
import { useAuth } from "@/contexts/AuthContext";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Snake Arena — Play, Compete, Spectate" },
      {
        name: "description",
        content:
          "A modern Snake game with walls and wrap-around modes, leaderboards, and live spectating.",
      },
    ],
  }),
  component: Home,
});

function Home() {
  const { user } = useAuth();
  return (
    <div className="min-h-screen flex flex-col">
      <AppHeader />
      <main className="flex-1 mx-auto max-w-5xl w-full px-4 py-16">
        <section className="text-center max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent text-accent-foreground text-xs font-medium mb-6">
            <span className="size-2 rounded-full bg-primary animate-pulse" /> Live multiplayer-ready
          </div>
          <h1 className="text-5xl sm:text-6xl font-black tracking-tight">Snake, but social.</h1>
          <p className="mt-4 text-lg text-muted-foreground">
            Two modes. Global leaderboards. Watch others play live.
          </p>
          <div className="mt-8 flex gap-3 justify-center">
            <Link
              to="/play"
              className="px-6 py-3 rounded-md bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition"
            >
              Play now
            </Link>
            <Link
              to="/watch"
              className="px-6 py-3 rounded-md border border-border hover:bg-accent transition"
            >
              Watch live
            </Link>
          </div>
          {!user && (
            <p className="mt-4 text-sm text-muted-foreground">
              <Link to="/auth" className="underline hover:text-foreground">
                Sign in
              </Link>{" "}
              to save your scores.
            </p>
          )}
        </section>

        <section className="mt-20 grid sm:grid-cols-2 gap-4">
          <ModeCard
            title="Walls"
            desc="Hit a wall, game over. Classic and unforgiving."
            badge="Hard"
          />
          <ModeCard title="Wrap" desc="Edges loop around. Plan in cycles." badge="Chill" />
        </section>
      </main>
    </div>
  );
}

function ModeCard({ title, desc, badge }: { title: string; desc: string; badge: string }) {
  return (
    <div className="p-6 rounded-xl border border-border bg-card">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold">{title}</h3>
        <span className="text-xs px-2 py-0.5 rounded-full bg-accent text-accent-foreground">
          {badge}
        </span>
      </div>
      <p className="mt-2 text-muted-foreground">{desc}</p>
    </div>
  );
}
