"use client";

import { useState } from "react";

import { useAuth } from "../../components/AuthProvider";
import { FeaturePage } from "../../components/FeaturePage";
import { useNotifier } from "../../components/NotificationCenter";
import { apiPost } from "../../lib/api";

export default function KnowledgePage(): React.ReactElement {
  const { token } = useAuth();
  const { notify } = useNotifier();
  const [query, setQuery] = useState("What policy covers procurement approval limits?");
  const [results, setResults] = useState("[]");

  const search = async (): Promise<void> => {
    try {
      const response = await apiPost("/knowledge/search", { query, top_k: 5 }, token);
      setResults(JSON.stringify(response, null, 2));
    } catch (error) {
      notify("Knowledge search failed", String(error));
    }
  };

  return (
    <FeaturePage title="Knowledge Base" description="Hybrid semantic + keyword retrieval with citations.">
      <div className="card flex gap-3">
        <input
          className="flex-1 rounded border border-slate-300/40 bg-transparent px-3 py-2"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <button type="button" className="rounded bg-emerald-600 px-3 py-2 text-sm text-white" onClick={search}>
          Search
        </button>
      </div>
      <pre className="card overflow-x-auto text-xs">{results}</pre>
    </FeaturePage>
  );
}
