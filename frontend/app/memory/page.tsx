"use client";

import { useState } from "react";

import { useAuth } from "../../components/AuthProvider";
import { FeaturePage } from "../../components/FeaturePage";
import { useNotifier } from "../../components/NotificationCenter";
import { apiGet, apiPost } from "../../lib/api";

export default function MemoryPage(): React.ReactElement {
  const { token } = useAuth();
  const { notify } = useNotifier();
  const [memoryKey, setMemoryKey] = useState("preferred_report_format");
  const [memoryValue, setMemoryValue] = useState('{"value":"pptx"}');
  const [items, setItems] = useState("[]");

  const save = async (): Promise<void> => {
    try {
      await apiPost("/memory", { scope: "preferences", key: memoryKey, value: JSON.parse(memoryValue) }, token);
      notify("Memory saved", memoryKey);
    } catch (error) {
      notify("Save failed", String(error));
    }
  };

  const load = async (): Promise<void> => {
    try {
      const response = await apiGet("/memory", token);
      setItems(JSON.stringify(response, null, 2));
    } catch (error) {
      notify("Load failed", String(error));
    }
  };

  return (
    <FeaturePage title="Memory" description="Short-term and long-term memory inspection and deletion controls.">
      <div className="card grid gap-2 md:grid-cols-3">
        <input className="rounded border border-slate-300/40 bg-transparent px-3 py-2" value={memoryKey} onChange={(event) => setMemoryKey(event.target.value)} />
        <input className="rounded border border-slate-300/40 bg-transparent px-3 py-2" value={memoryValue} onChange={(event) => setMemoryValue(event.target.value)} />
        <div className="flex gap-2">
          <button type="button" className="rounded bg-emerald-600 px-3 py-2 text-sm text-white" onClick={save}>Save</button>
          <button type="button" className="rounded border border-slate-300/40 px-3 py-2 text-sm" onClick={load}>Load</button>
        </div>
      </div>
      <pre className="card overflow-x-auto text-xs">{items}</pre>
    </FeaturePage>
  );
}
