"use client";

import { useState } from "react";

import { useAuth } from "../../components/AuthProvider";
import { FeaturePage } from "../../components/FeaturePage";
import { useNotifier } from "../../components/NotificationCenter";
import { apiPost } from "../../lib/api";

export default function SettingsPage(): React.ReactElement {
  const { token } = useAuth();
  const { notify } = useNotifier();
  const [scope, setScope] = useState("platform");
  const [key, setKey] = useState("default_timezone");
  const [value, setValue] = useState('{"value":"Asia/Kolkata"}');

  const save = async (): Promise<void> => {
    try {
      await apiPost("/settings", { scope, key, value: JSON.parse(value) }, token);
      notify("Setting saved", `${scope}.${key}`);
    } catch (error) {
      notify("Save failed", String(error));
    }
  };

  return (
    <FeaturePage title="Settings" description="Organization-level settings, policy knobs, and runtime defaults.">
      <div className="card grid gap-2 md:grid-cols-4">
        <input className="rounded border border-slate-300/40 bg-transparent px-3 py-2" value={scope} onChange={(event) => setScope(event.target.value)} />
        <input className="rounded border border-slate-300/40 bg-transparent px-3 py-2" value={key} onChange={(event) => setKey(event.target.value)} />
        <input className="rounded border border-slate-300/40 bg-transparent px-3 py-2" value={value} onChange={(event) => setValue(event.target.value)} />
        <button type="button" className="rounded bg-emerald-600 px-3 py-2 text-sm text-white" onClick={save}>
          Save Setting
        </button>
      </div>
    </FeaturePage>
  );
}
