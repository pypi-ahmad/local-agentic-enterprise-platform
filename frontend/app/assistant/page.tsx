"use client";

import { useState } from "react";

import { FeaturePage } from "../../components/FeaturePage";
import { apiPost } from "../../lib/api";
import { useAuth } from "../../components/AuthProvider";
import { useNotifier } from "../../components/NotificationCenter";

export default function AssistantPage(): React.ReactElement {
  const { token } = useAuth();
  const { notify } = useNotifier();
  const [task, setTask] = useState("Summarize this business request and suggest action plan");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const run = async (): Promise<void> => {
    if (!token) {
      notify("Auth required", "Login first from Dashboard page.");
      return;
    }
    setLoading(true);
    setResponse("");
    try {
      const result = await apiPost<{ output: { result?: string } }>(
        "/agents/execute",
        {
          agent_name: "workflow",
          task,
          payload: { request: task },
          context: {},
          require_approval: false
        },
        token
      );
      const full = result.output.result ?? JSON.stringify(result.output);
      for (let index = 0; index < full.length; index += 8) {
        setResponse((current) => current + full.slice(index, index + 8));
        await new Promise((resolve) => setTimeout(resolve, 12));
      }
    } catch (error) {
      notify("Assistant failed", String(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <FeaturePage title="AI Assistant" description="Streaming multi-agent business assistant with supervisor coordination.">
      <div className="card space-y-3">
        <textarea
          className="h-24 w-full rounded border border-slate-300/40 bg-transparent p-3"
          value={task}
          onChange={(event) => setTask(event.target.value)}
        />
        <button type="button" onClick={run} className="rounded bg-emerald-600 px-3 py-2 text-sm text-white">
          {loading ? "Running..." : "Run Assistant"}
        </button>
      </div>
      <div className="card min-h-40 whitespace-pre-wrap text-sm text-slate-700 dark:text-slate-200">{response}</div>
    </FeaturePage>
  );
}
