"use client";

import { useState } from "react";

import { apiPost } from "../lib/api";
import { useAuth } from "./AuthProvider";
import { useNotifier } from "./NotificationCenter";

type LoginResponse = {
  access_token: string;
  token_type: string;
  roles: string[];
};

export function AuthPanel(): React.ReactElement {
  const { token, setToken, clearToken } = useAuth();
  const { notify } = useNotifier();
  const [username, setUsername] = useState("local-admin");
  const [password, setPassword] = useState("change-me-now");

  const login = async (): Promise<void> => {
    try {
      const response = await apiPost<LoginResponse>("/auth/login", { username, password });
      setToken(response.access_token);
      notify("Authentication", "Session token saved.");
    } catch (error) {
      notify("Login failed", String(error));
    }
  };

  return (
    <div className="card flex flex-wrap items-end gap-3">
      <div className="text-xs">
        <div className="font-semibold">Auth Session</div>
        <div className="text-slate-500 dark:text-slate-300">
          {token ? "Authenticated" : "Not authenticated"}
        </div>
      </div>
      <input
        className="rounded border border-slate-300/40 px-3 py-2 text-sm"
        value={username}
        onChange={(event) => setUsername(event.target.value)}
        placeholder="username"
      />
      <input
        className="rounded border border-slate-300/40 px-3 py-2 text-sm"
        value={password}
        type="password"
        onChange={(event) => setPassword(event.target.value)}
        placeholder="password"
      />
      <button type="button" className="rounded bg-emerald-600 px-3 py-2 text-sm text-white" onClick={login}>
        Login
      </button>
      <button type="button" className="rounded border border-slate-300/40 px-3 py-2 text-sm" onClick={clearToken}>
        Logout
      </button>
    </div>
  );
}
