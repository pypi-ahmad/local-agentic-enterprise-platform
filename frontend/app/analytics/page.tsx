"use client";

import { useMemo, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { FeaturePage } from "../../components/FeaturePage";

export default function AnalyticsPage(): React.ReactElement {
  const [series] = useState([38, 41, 39, 52, 57, 54, 60, 62, 58, 68]);
  const data = useMemo(
    () => series.map((value, index) => ({ day: `D${index + 1}`, value })),
    [series]
  );

  return (
    <FeaturePage title="Analytics" description="Descriptive analytics, trends, anomaly cues, and forecasting baseline.">
      <div className="card h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={3} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="card">KPI Growth: <b>+12%</b></div>
        <div className="card">Anomaly Alerts: <b>2</b></div>
        <div className="card">Forecast Confidence: <b>0.81</b></div>
      </div>
    </FeaturePage>
  );
}
