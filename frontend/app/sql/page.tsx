"use client";

import { useState } from "react";

import { useAuth } from "../../components/AuthProvider";
import { FeaturePage } from "../../components/FeaturePage";
import { useNotifier } from "../../components/NotificationCenter";
import { apiPost } from "../../lib/api";

export default function SQLPage(): React.ReactElement {
  const { token } = useAuth();
  const { notify } = useNotifier();
  const [prompt, setPrompt] = useState("Show top 10 recent workflow runs with status counts.");
  const [sql, setSql] = useState("");
  const [explanation, setExplanation] = useState("");
  const [result, setResult] = useState("{}");

  const generateSQL = async (): Promise<void> => {
    try {
      const generated = await apiPost<{ sql: string; explanation: string }>(
        "/sql/generate",
        { prompt, dialect: "postgres", schema_hint: "workflow_runs(id,status,created_at)" },
        token
      );
      setSql(generated.sql);
      setExplanation(generated.explanation);
    } catch (error) {
      notify("SQL generation failed", String(error));
    }
  };

  const executeSQL = async (): Promise<void> => {
    try {
      const executed = await apiPost("/sql/execute", { sql, dry_run: false, confirm: true }, token);
      setResult(JSON.stringify(executed, null, 2));
    } catch (error) {
      notify("SQL execution failed", String(error));
    }
  };

  return (
    <FeaturePage title="SQL Workspace" description="Natural language to SQL with explanations and destructive query approvals.">
      <div className="card space-y-3">
        <textarea
          className="h-24 w-full rounded border border-slate-300/40 bg-transparent p-3"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
        />
        <button type="button" className="rounded bg-emerald-600 px-3 py-2 text-sm text-white" onClick={generateSQL}>
          Generate SQL
        </button>
        <textarea
          className="h-24 w-full rounded border border-slate-300/40 bg-transparent p-3"
          value={sql}
          onChange={(event) => setSql(event.target.value)}
        />
        <div className="text-sm text-slate-500 dark:text-slate-300">{explanation}</div>
        <button type="button" className="rounded border border-slate-300/40 px-3 py-2 text-sm" onClick={executeSQL}>
          Execute (Confirmed)
        </button>
      </div>
      <pre className="card overflow-x-auto text-xs">{result}</pre>
    </FeaturePage>
  );
}
