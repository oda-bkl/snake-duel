import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { getApi } from "@/services/api";
import type { User } from "@/services/types";

interface AuthCtx {
  user: User | null;
  loading: boolean;
  login: (u: string, p: string) => Promise<void>;
  signup: (u: string, p: string) => Promise<void>;
  logout: () => Promise<void>;
}

const Ctx = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getApi().currentSession().then((s) => {
      setUser(s?.user ?? null);
      setLoading(false);
    });
  }, []);

  const value: AuthCtx = {
    user,
    loading,
    async login(u, p) {
      const s = await getApi().login(u, p);
      setUser(s.user);
    },
    async signup(u, p) {
      const s = await getApi().signup(u, p);
      setUser(s.user);
    },
    async logout() {
      await getApi().logout();
      setUser(null);
    },
  };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const v = useContext(Ctx);
  if (!v) throw new Error("useAuth must be used within AuthProvider");
  return v;
}
