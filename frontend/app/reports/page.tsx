"use client";

import { useState } from "react";

import { useAuth } from "../../components/AuthProvider";
import { FeaturePage } from "../../components/FeaturePage";
import { useNotifier } from "../../components/NotificationCenter";
import { apiPost } from "../../lib/api";

export default function ReportsPage(): React.ReactElement {
  const { token } = useAuth();
  const { notify } = useNotifier();
  const [reportId, setReportId] = useState<number | null>(null);
  const [exportPath, setExportPath] = useState("");

  const createReport = async (): Promise<void> => {
    try {
      const created = await apiPost<{ id: number }>(
        "/reports",
        {
          name: "Weekly Executive Summary",
          report_type: "weekly",
          payload: {
            title: "Weekly Executive Summary",
            kpi_growth: "12%",
            risk_level: "low",
            top_action: "Scale outbound automation"
          }
        },
        token
      );
      setReportId(created.id);
      notify("Report created", `Report #${created.id} ready for export.`);
    } catch (error) {
      notify("Report create failed", String(error));
    }
  };

  const exportReport = async (fmt: "pdf" | "xlsx" | "pptx"): Promise<void> => {
    if (!reportId) {
      notify("No report", "Create report first.");
      return;
    }
    try {
      const response = await apiPost<{ path: string }>(`/reports/${reportId}/export/${fmt}`, {}, token);
      setExportPath(response.path);
    } catch (error) {
      notify("Export failed", String(error));
    }
  };

  return (
    <FeaturePage title="Reports" description="Daily/weekly/monthly reports, KPI summaries, PDF/Excel/PPT exports.">
      <div className="card flex flex-wrap gap-2">
        <button type="button" className="rounded bg-emerald-600 px-3 py-2 text-sm text-white" onClick={createReport}>
          Create Weekly Report
        </button>
        <button type="button" className="rounded border border-slate-300/40 px-3 py-2 text-sm" onClick={() => exportReport("pdf")}>
          Export PDF
        </button>
        <button type="button" className="rounded border border-slate-300/40 px-3 py-2 text-sm" onClick={() => exportReport("xlsx")}>
          Export Excel
        </button>
        <button type="button" className="rounded border border-slate-300/40 px-3 py-2 text-sm" onClick={() => exportReport("pptx")}>
          Export PowerPoint
        </button>
      </div>
      <div className="card text-sm">
        <div>Report ID: {reportId ?? "none"}</div>
        <div>Last export path: {exportPath || "none"}</div>
      </div>
    </FeaturePage>
  );
}
