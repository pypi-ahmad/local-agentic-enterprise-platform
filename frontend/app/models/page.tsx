"use client";

import { useState } from "react";

import { useAuth } from "../../components/AuthProvider";
import { FeaturePage } from "../../components/FeaturePage";
import { useNotifier } from "../../components/NotificationCenter";
import { apiGet } from "../../lib/api";

export default function ModelsPage(): React.ReactElement {
  const { token } = useAuth();
  const { notify } = useNotifier();
  const [models, setModels] = useState("{}");

  const load = async (): Promise<void> => {
    try {
      const response = await apiGet("/system/models", token);
      setModels(JSON.stringify(response, null, 2));
    } catch (error) {
      notify("Model fetch failed", String(error));
    }
  };

  return (
    <FeaturePage title="Model Manager" description="Installed Ollama models, routing decisions, and fallback chain visibility.">
      <div className="card">
        <button type="button" className="rounded bg-emerald-600 px-3 py-2 text-sm text-white" onClick={load}>
          Refresh Models
        </button>
      </div>
      <pre className="card overflow-x-auto text-xs">{models}</pre>
    </FeaturePage>
  );
}
