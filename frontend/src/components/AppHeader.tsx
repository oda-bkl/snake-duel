import { Link, useRouter } from "@tanstack/react-router";
import { Moon, Sun } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/hooks/useTheme";
import { Button } from "@/components/ui/button";

export function AppHeader() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const { theme, toggle } = useTheme();
  return (
    <header className="border-b border-border bg-card/40 backdrop-blur sticky top-0 z-10">
      <div className="mx-auto max-w-5xl px-4 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-bold text-lg tracking-tight">
          <span className="text-primary">▰▰</span>
          <span>Snake Arena</span>
        </Link>
        <nav className="flex items-center gap-1 text-sm">
          <Link to="/play" className="px-3 py-1.5 rounded-md hover:bg-accent" activeProps={{ className: "px-3 py-1.5 rounded-md bg-accent" }}>Play</Link>
          <Link to="/leaderboard" className="px-3 py-1.5 rounded-md hover:bg-accent" activeProps={{ className: "px-3 py-1.5 rounded-md bg-accent" }}>Leaderboard</Link>
          <Link to="/watch" className="px-3 py-1.5 rounded-md hover:bg-accent" activeProps={{ className: "px-3 py-1.5 rounded-md bg-accent" }}>Watch</Link>
          <Button size="sm" variant="ghost" onClick={toggle} aria-label="Toggle theme">
            {theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
          </Button>
          {user ? (
            <div className="flex items-center gap-2 ml-2 pl-2 border-l border-border">
              <span className="text-muted-foreground hidden sm:inline">@{user.username}</span>
              <Button
                size="sm"
                variant="ghost"
                onClick={async () => {
                  try {
                    await logout();
                    router.navigate({ to: "/" });
                  } catch {
                    toast.error("Failed to log out. Try again.");
                  }
                }}
              >
                Log out
              </Button>
            </div>
          ) : (
            <Link to="/auth" className="ml-2 px-3 py-1.5 rounded-md bg-primary text-primary-foreground font-medium">
              Sign in
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
