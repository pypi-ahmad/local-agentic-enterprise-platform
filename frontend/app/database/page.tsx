"use client";

import { useState } from "react";

import { useAuth } from "../../components/AuthProvider";
import { FeaturePage } from "../../components/FeaturePage";
import { useNotifier } from "../../components/NotificationCenter";
import { apiGet } from "../../lib/api";

export default function DatabasePage(): React.ReactElement {
  const { token } = useAuth();
  const { notify } = useNotifier();
  const [tables, setTables] = useState<string[]>([]);

  const loadTables = async (): Promise<void> => {
    try {
      const result = await apiGet<{ tables: string[] }>("/database/schemas", token);
      setTables(result.tables);
    } catch (error) {
      notify("Schema fetch failed", String(error));
    }
  };

  return (
    <FeaturePage title="Database Explorer" description="Schema discovery, table previews, and safe query path.">
      <div className="card">
        <button type="button" className="rounded bg-emerald-600 px-3 py-2 text-sm text-white" onClick={loadTables}>
          Discover Tables
        </button>
      </div>
      <div className="card">
        <div className="font-semibold">Tables</div>
        <ul className="mt-2 list-disc pl-5 text-sm">
          {tables.map((table) => (
            <li key={table}>{table}</li>
          ))}
        </ul>
      </div>
    </FeaturePage>
  );
}
