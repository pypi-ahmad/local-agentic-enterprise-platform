"use client";

import { useEffect, useState } from "react";

import { useAuth } from "../../components/AuthProvider";
import { FeaturePage } from "../../components/FeaturePage";
import { apiGet } from "../../lib/api";

export default function MonitoringPage(): React.ReactElement {
  const { token } = useAuth();
  const [snapshot, setSnapshot] = useState("{}");

  useEffect(() => {
    if (!token) {
      return;
    }
    const tick = async (): Promise<void> => {
      const data = await apiGet("/system/monitoring", token);
      setSnapshot(JSON.stringify(data, null, 2));
    };
    void tick();
    const interval = setInterval(() => {
      void tick();
    }, 7000);
    return () => clearInterval(interval);
  }, [token]);

  return (
    <FeaturePage title="System Monitoring" description="Live CPU, memory, GPU utilization, and runtime diagnostics.">
      <pre className="card overflow-x-auto text-xs">{snapshot}</pre>
    </FeaturePage>
  );
}
