"use client";

import { useState } from "react";

import { useAuth } from "../../components/AuthProvider";
import { FeaturePage } from "../../components/FeaturePage";
import { useNotifier } from "../../components/NotificationCenter";
import { apiGet } from "../../lib/api";

export default function AgentsPage(): React.ReactElement {
  const { token } = useAuth();
  const { notify } = useNotifier();
  const [executions, setExecutions] = useState("[]");

  const load = async (): Promise<void> => {
    try {
      const response = await apiGet("/agents/executions", token);
      setExecutions(JSON.stringify(response, null, 2));
    } catch (error) {
      notify("Execution load failed", String(error));
    }
  };

  return (
    <FeaturePage title="Agent Activity" description="Execution graph, latency traces, and outcome audit for each agent run.">
      <div className="card">
        <button type="button" className="rounded bg-emerald-600 px-3 py-2 text-sm text-white" onClick={load}>
          Load Executions
        </button>
      </div>
      <pre className="card overflow-x-auto text-xs">{executions}</pre>
    </FeaturePage>
  );
}
