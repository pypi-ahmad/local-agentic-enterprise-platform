"use client";

import { useMemo } from "react";
import ReactFlow, { Background, Controls, Edge, Node } from "reactflow";
import "reactflow/dist/style.css";

import { FeaturePage } from "../../components/FeaturePage";

export default function WorkflowPage(): React.ReactElement {
  const nodes: Node[] = useMemo(
    () => [
      { id: "email", data: { label: "Email Agent" }, position: { x: 50, y: 100 } },
      { id: "priority", data: { label: "Priority Classifier" }, position: { x: 260, y: 100 } },
      { id: "planner", data: { label: "Supervisor Planner" }, position: { x: 500, y: 100 } },
      { id: "db", data: { label: "Database Update" }, position: { x: 760, y: 100 } },
      { id: "notify", data: { label: "Notification" }, position: { x: 980, y: 100 } }
    ],
    []
  );
  const edges: Edge[] = useMemo(
    () => [
      { id: "e1", source: "email", target: "priority", animated: true },
      { id: "e2", source: "priority", target: "planner", animated: true },
      { id: "e3", source: "planner", target: "db", animated: true },
      { id: "e4", source: "db", target: "notify", animated: true }
    ],
    []
  );

  return (
    <FeaturePage title="Workflow Builder" description="Visual workflow orchestration with branching, retries, and approvals.">
      <div className="card h-[560px]">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background color="#64748b" gap={20} />
          <Controls />
        </ReactFlow>
      </div>
    </FeaturePage>
  );
}
