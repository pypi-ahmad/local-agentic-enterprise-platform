"use client";

import { useState } from "react";

import { useAuth } from "../../components/AuthProvider";
import { FeaturePage } from "../../components/FeaturePage";
import { useNotifier } from "../../components/NotificationCenter";
import { apiPost } from "../../lib/api";

export default function CalendarPage(): React.ReactElement {
  const { token } = useAuth();
  const { notify } = useNotifier();
  const [context, setContext] = useState("Quarterly roadmap sync with engineering and product teams.");
  const [agenda, setAgenda] = useState("");

  const generateAgenda = async (): Promise<void> => {
    try {
      const result = await apiPost<{ agenda: string }>("/calendar/agenda", { context }, token);
      setAgenda(result.agenda);
    } catch (error) {
      notify("Agenda generation failed", String(error));
    }
  };

  return (
    <FeaturePage title="Calendar" description="Scheduling, conflicts, recurring reminders, meeting agendas and summaries.">
      <div className="card space-y-3">
        <textarea
          className="h-24 w-full rounded border border-slate-300/40 bg-transparent p-3"
          value={context}
          onChange={(event) => setContext(event.target.value)}
        />
        <button type="button" className="rounded bg-emerald-600 px-3 py-2 text-sm text-white" onClick={generateAgenda}>
          Generate Agenda
        </button>
      </div>
      <div className="card min-h-40 whitespace-pre-wrap text-sm">{agenda}</div>
    </FeaturePage>
  );
}
