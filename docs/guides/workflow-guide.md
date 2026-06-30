# Workflow Guide

## Workflow Definition

A workflow is a directed graph:
- Nodes: `agent`, `condition`, `approval`, `notification`, `terminal`
- Edges: optional conditions for branching

## Execution Features

- Sequential execution through graph edges.
- Parallel execution for same-frontier nodes.
- Conditional branching via safe expression evaluation.
- Retry support per agent node.
- Human approval gates for sensitive steps.
- Timeline persistence per workflow run.

## Reusable Templates

Set `is_template=true` on definitions and duplicate for org workflows.
