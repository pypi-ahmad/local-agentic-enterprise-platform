"use client";

import { useEffect, useState } from "react";

import { AuthPanel } from "../components/AuthPanel";
import { FeaturePage } from "../components/FeaturePage";
import { apiGet } from "../lib/api";
import { useAuth } from "../components/AuthProvider";

export default function DashboardPage(): React.ReactElement {
  const { token } = useAuth();
  const [monitoring, setMonitoring] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }
    apiGet<Record<string, unknown>>("/system/monitoring", token)
      .then(setMonitoring)
      .catch(() => setMonitoring(null));
  }, [token]);

  return (
    <FeaturePage
      title="Dashboard"
      description="Enterprise control center for agents, workflows, KPIs, and infrastructure health."
    >
      <AuthPanel />
      <div className="grid gap-4 md:grid-cols-3">
        <div className="card">
          <div className="text-xs text-slate-500 dark:text-slate-300">Active Agents</div>
          <div className="mt-2 text-3xl font-bold">15</div>
          <span className="badge badge-ok">Supervisor online</span>
        </div>
        <div className="card">
          <div className="text-xs text-slate-500 dark:text-slate-300">Workflow Runs (24h)</div>
          <div className="mt-2 text-3xl font-bold">128</div>
          <span className="badge badge-warn">3 pending approval</span>
        </div>
        <div className="card">
          <div className="text-xs text-slate-500 dark:text-slate-300">Model Routing</div>
          <div className="mt-2 text-3xl font-bold">Dynamic</div>
          <span className="badge badge-ok">GPU-first fallback ready</span>
        </div>
      </div>
      <div className="card">
        <div className="font-semibold">System Snapshot</div>
        <pre className="mt-2 overflow-x-auto text-xs text-slate-500 dark:text-slate-300">
          {JSON.stringify(monitoring, null, 2)}
        </pre>
      </div>
    </FeaturePage>
  );
}
