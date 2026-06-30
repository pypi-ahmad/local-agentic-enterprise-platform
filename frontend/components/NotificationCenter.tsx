"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";

type Notification = {
  id: number;
  title: string;
  message: string;
};

type NotificationContextValue = {
  notify: (title: string, message: string) => void;
};

const NotificationContext = createContext<NotificationContextValue | null>(null);

export function useNotifier(): NotificationContextValue {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error("useNotifier must be used within NotificationProvider");
  }
  return context;
}

export function NotificationProvider({ children }: { children: React.ReactNode }): React.ReactElement {
  const [items, setItems] = useState<Notification[]>([]);

  const notify = useCallback((title: string, message: string) => {
    setItems((current) => {
      const next = [...current, { id: Date.now(), title, message }];
      return next.slice(-5);
    });
  }, []);

  const value = useMemo(() => ({ notify }), [notify]);

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <div className="fixed right-4 top-4 z-50 flex w-80 flex-col gap-2">
        {items.map((item) => (
          <div key={item.id} className="card border-l-4 border-l-emerald-500 shadow-lg">
            <div className="text-sm font-semibold">{item.title}</div>
            <div className="text-xs text-slate-500 dark:text-slate-300">{item.message}</div>
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  );
}
