import { useEffect, useState } from "react";

type Theme = "light" | "dark";

const STORAGE_KEY = "snake.theme";

export function useTheme() {
  // The blocking script in <head> already applied the correct class before
  // React loaded, so we read the DOM as the source of truth after hydration.
  // Start with "dark" to match the SSR default (no flash before the effect runs).
  const [theme, setTheme] = useState<Theme>("dark");

  useEffect(() => {
    setTheme(document.documentElement.classList.contains("dark") ? "dark" : "light");
  }, []);

  const toggle = () => {
    setTheme((prev) => {
      const next = prev === "dark" ? "light" : "dark";
      document.documentElement.classList.toggle("dark", next === "dark");
      localStorage.setItem(STORAGE_KEY, next);
      return next;
    });
  };

  return { theme, toggle };
}
