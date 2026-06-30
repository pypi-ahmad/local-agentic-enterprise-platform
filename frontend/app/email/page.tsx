"use client";

import { useState } from "react";

import { useAuth } from "../../components/AuthProvider";
import { FeaturePage } from "../../components/FeaturePage";
import { useNotifier } from "../../components/NotificationCenter";
import { apiPost } from "../../lib/api";

export default function EmailPage(): React.ReactElement {
  const { token } = useAuth();
  const { notify } = useNotifier();
  const [thread, setThread] = useState("Client asked for delivery timeline update.");
  const [draft, setDraft] = useState("");

  const createDraft = async (): Promise<void> => {
    try {
      const result = await apiPost<{ draft: string; send_allowed: string }>(
        "/email/draft-reply",
        { email_thread: thread, tone: "professional" },
        token
      );
      setDraft(`${result.draft}\n\nSend allowed: ${result.send_allowed}`);
    } catch (error) {
      notify("Email draft failed", String(error));
    }
  };

  return (
    <FeaturePage title="Email" description="Inbox summarization, priority classification, drafting, reminders, attachment actions.">
      <div className="card space-y-3">
        <textarea
          className="h-28 w-full rounded border border-slate-300/40 bg-transparent p-3"
          value={thread}
          onChange={(event) => setThread(event.target.value)}
        />
        <button type="button" className="rounded bg-emerald-600 px-3 py-2 text-sm text-white" onClick={createDraft}>
          Draft Reply (Approval-Only Send Policy)
        </button>
      </div>
      <div className="card min-h-40 whitespace-pre-wrap text-sm">{draft}</div>
    </FeaturePage>
  );
}
