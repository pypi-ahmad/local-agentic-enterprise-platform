"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

const navItems = [
  ["Dashboard", "/"],
  ["AI Assistant", "/assistant"],
  ["Email", "/email"],
  ["Calendar", "/calendar"],
  ["Reports", "/reports"],
  ["Analytics", "/analytics"],
  ["Database Explorer", "/database"],
  ["SQL Workspace", "/sql"],
  ["Workflow Builder", "/workflows"],
  ["Documents", "/documents"],
  ["Knowledge Base", "/knowledge"],
  ["Memory", "/memory"],
  ["Agent Activity", "/agents"],
  ["Logs", "/logs"],
  ["Settings", "/settings"],
  ["Model Manager", "/models"],
  ["System Monitoring", "/monitoring"]
] as const;

const quickNav: Record<string, string> = {
  d: "/",
  a: "/assistant",
  e: "/email",
  c: "/calendar",
  r: "/reports",
  s: "/sql",
  w: "/workflows",
  m: "/models"
};

export function AppShell({ children }: { children: React.ReactNode }): React.ReactElement {
  const pathname = usePathname();
  const router = useRouter();
  const [dark, setDark] = useState(true);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent): void => {
      if (event.altKey && quickNav[event.key]) {
        router.push(quickNav[event.key] as never);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [router]);

  const shortcuts = useMemo(
    () => ["Alt+d Dashboard", "Alt+a Assistant", "Alt+s SQL", "Alt+w Workflow", "Alt+m Models"],
    []
  );

  return (
    <div className="shell-grid">
      <aside className="border-r border-slate-200/20 bg-slate-950/80 p-4 text-slate-100 backdrop-blur-sm">
        <h1 className="text-lg font-bold">LAEP Console</h1>
        <p className="mt-1 text-xs text-slate-400">Local Agentic Enterprise</p>
        <nav className="mt-6 flex flex-col gap-1">
          {navItems.map(([label, href]) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`rounded-md px-3 py-2 text-sm transition ${
                  active ? "bg-emerald-500/20 text-emerald-300" : "text-slate-300 hover:bg-slate-800"
                }`}
              >
                {label}
              </Link>
            );
          })}
        </nav>
        <div className="mt-6 text-xs text-slate-400">
          <div className="font-semibold text-slate-200">Shortcuts</div>
          <ul className="mt-2 list-disc pl-4">
            {shortcuts.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </aside>
      <main className="min-h-screen p-5 md:p-8">
        <header className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="text-lg font-semibold">Business Automation Platform</div>
            <div className="text-xs text-slate-500 dark:text-slate-400">GPU-first local enterprise agent runtime</div>
          </div>
          <button
            type="button"
            className="rounded-md border border-slate-300/40 px-3 py-1 text-sm"
            onClick={() => setDark((value) => !value)}
          >
            {dark ? "Light" : "Dark"} mode
          </button>
        </header>
        {children}
      </main>
    </div>
  );
}
