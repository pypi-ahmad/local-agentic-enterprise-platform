"use client";

import { DragEvent, useState } from "react";

import { useAuth } from "../../components/AuthProvider";
import { FeaturePage } from "../../components/FeaturePage";
import { useNotifier } from "../../components/NotificationCenter";
import { API_BASE } from "../../lib/api";

export default function DocumentsPage(): React.ReactElement {
  const { token } = useAuth();
  const { notify } = useNotifier();
  const [uploaded, setUploaded] = useState<string>("");

  const uploadFile = async (file: File): Promise<void> => {
    const form = new FormData();
    form.append("file", file);
    try {
      const response = await fetch(`${API_BASE}/documents/upload`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        body: form
      });
      const body = await response.json();
      if (!response.ok) {
        throw new Error(JSON.stringify(body));
      }
      setUploaded(JSON.stringify(body));
      notify("Upload complete", `Document indexed: ${file.name}`);
    } catch (error) {
      notify("Upload failed", String(error));
    }
  };

  const onDrop = async (event: DragEvent<HTMLDivElement>): Promise<void> => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      await uploadFile(file);
    }
  };

  return (
    <FeaturePage title="Documents" description="Drag-and-drop upload, OCR extraction, and knowledge indexing.">
      <div
        className="card flex h-44 items-center justify-center border-2 border-dashed border-emerald-500/40 text-sm"
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          void onDrop(event);
        }}
      >
        Drop file here to upload and index
      </div>
      <div className="card text-xs whitespace-pre-wrap">{uploaded || "No uploads yet"}</div>
    </FeaturePage>
  );
}
