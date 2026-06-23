import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";

export const Route = createFileRoute("/auth")({
  head: () => ({ meta: [{ title: "Sign in — Snake Arena" }] }),
  component: AuthPage,
});

function AuthPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-background">
      <div className="w-full max-w-md">
        <Link to="/" className="block text-center font-bold text-2xl mb-6">
          ▰▰ Snake Arena
        </Link>
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
          <Tabs defaultValue="login">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Log in</TabsTrigger>
              <TabsTrigger value="signup">Sign up</TabsTrigger>
            </TabsList>
            <TabsContent value="login">
              <LoginForm />
            </TabsContent>
            <TabsContent value="signup">
              <SignupForm />
            </TabsContent>
          </Tabs>
          <p className="mt-4 text-xs text-muted-foreground text-center">
            Demo account: <code className="font-mono">demo</code> /{" "}
            <code className="font-mono">demo</code>
          </p>
        </div>
      </div>
    </div>
  );
}

function LoginForm() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [u, setU] = useState("demo");
  const [p, setP] = useState("demo");
  const [busy, setBusy] = useState(false);
  return (
    <form
      className="space-y-4 mt-4"
      onSubmit={async (e) => {
        e.preventDefault();
        setBusy(true);
        try {
          await login(u, p);
          toast.success("Welcome back!");
          nav({ to: "/play" });
        } catch (err) {
          toast.error((err as Error).message);
        } finally {
          setBusy(false);
        }
      }}
    >
      <div>
        <Label htmlFor="lu">Username</Label>
        <Input
          id="lu"
          value={u}
          onChange={(e) => setU(e.target.value)}
          autoComplete="username"
          required
        />
      </div>
      <div>
        <Label htmlFor="lp">Password</Label>
        <Input
          id="lp"
          type="password"
          value={p}
          onChange={(e) => setP(e.target.value)}
          autoComplete="current-password"
          required
        />
      </div>
      <Button type="submit" className="w-full" disabled={busy}>
        {busy ? "Signing in…" : "Log in"}
      </Button>
    </form>
  );
}

function SignupForm() {
  const { signup } = useAuth();
  const nav = useNavigate();
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <form
      className="space-y-4 mt-4"
      onSubmit={async (e) => {
        e.preventDefault();
        setBusy(true);
        try {
          await signup(u, p);
          toast.success("Account created!");
          nav({ to: "/play" });
        } catch (err) {
          toast.error((err as Error).message);
        } finally {
          setBusy(false);
        }
      }}
    >
      <div>
        <Label htmlFor="su">Username</Label>
        <Input id="su" value={u} onChange={(e) => setU(e.target.value)} required minLength={2} />
      </div>
      <div>
        <Label htmlFor="sp">Password</Label>
        <Input
          id="sp"
          type="password"
          value={p}
          onChange={(e) => setP(e.target.value)}
          required
          minLength={3}
        />
      </div>
      <Button type="submit" className="w-full" disabled={busy}>
        {busy ? "Creating…" : "Create account"}
      </Button>
    </form>
  );
}
