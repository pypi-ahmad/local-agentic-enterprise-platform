"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

type AuthContextValue = {
  token: string;
  setToken: (value: string) => void;
  clearToken: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }): React.ReactElement {
  const [token, setTokenState] = useState("");

  useEffect(() => {
    const existing = localStorage.getItem("laep_token") ?? "";
    setTokenState(existing);
  }, []);

  const setToken = (value: string): void => {
    localStorage.setItem("laep_token", value);
    setTokenState(value);
  };

  const clearToken = (): void => {
    localStorage.removeItem("laep_token");
    setTokenState("");
  };

  const value = useMemo(() => ({ token, setToken, clearToken }), [token]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
