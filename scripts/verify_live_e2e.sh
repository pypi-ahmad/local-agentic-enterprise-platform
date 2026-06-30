#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
WEB_URL="${WEB_URL:-http://127.0.0.1:3000}"
RUN_TS="${RUN_TS:-$(date +%Y%m%d_%H%M%S)}"
OUT_DIR="${OUT_DIR:-artifacts/e2e/${RUN_TS}}"

mkdir -p "${OUT_DIR}"
echo "${OUT_DIR}" > artifacts/e2e/latest_run_dir.txt

api_call() {
  local name="$1"
  local method="$2"
  local path="$3"
  local body="${4:-}"
  local token="${5:-}"
  local output="${OUT_DIR}/${name}.json"
  local status=""

  if [[ -n "${body}" ]]; then
    if [[ -n "${token}" ]]; then
      status="$(curl -sS -o "${output}" -w "%{http_code}" -X "${method}" "${BASE_URL}${path}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${token}" \
        --data "${body}")"
    else
      status="$(curl -sS -o "${output}" -w "%{http_code}" -X "${method}" "${BASE_URL}${path}" \
        -H "Content-Type: application/json" \
        --data "${body}")"
    fi
  else
    if [[ -n "${token}" ]]; then
      status="$(curl -sS -o "${output}" -w "%{http_code}" -X "${method}" "${BASE_URL}${path}" \
        -H "Authorization: Bearer ${token}")"
    else
      status="$(curl -sS -o "${output}" -w "%{http_code}" -X "${method}" "${BASE_URL}${path}")"
    fi
  fi

  if [[ ! "${status}" =~ ^2 ]]; then
    echo "API call failed: ${name} ${method} ${path} -> HTTP ${status}" >&2
    cat "${output}" >&2 || true
    exit 1
  fi
}

api_expect_status() {
  local name="$1"
  local method="$2"
  local path="$3"
  local expected="$4"
  local body="${5:-}"
  local token="${6:-}"
  local output="${OUT_DIR}/${name}.json"
  local status=""

  if [[ -n "${body}" ]]; then
    if [[ -n "${token}" ]]; then
      status="$(curl -sS -o "${output}" -w "%{http_code}" -X "${method}" "${BASE_URL}${path}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${token}" \
        --data "${body}")"
    else
      status="$(curl -sS -o "${output}" -w "%{http_code}" -X "${method}" "${BASE_URL}${path}" \
        -H "Content-Type: application/json" \
        --data "${body}")"
    fi
  else
    if [[ -n "${token}" ]]; then
      status="$(curl -sS -o "${output}" -w "%{http_code}" -X "${method}" "${BASE_URL}${path}" \
        -H "Authorization: Bearer ${token}")"
    else
      status="$(curl -sS -o "${output}" -w "%{http_code}" -X "${method}" "${BASE_URL}${path}")"
    fi
  fi

  if [[ "${status}" != "${expected}" ]]; then
    echo "Expected HTTP ${expected}, got ${status}: ${name} ${method} ${path}" >&2
    cat "${output}" >&2 || true
    exit 1
  fi
}

json_get() {
  local file="$1"
  local path="$2"
  python3 - "$file" "$path" <<'PY'
import json
import sys
from pathlib import Path

obj = json.loads(Path(sys.argv[1]).read_text())
parts = sys.argv[2].split(".")
current = obj
for part in parts:
    if part == "":
        continue
    if part.isdigit():
        current = current[int(part)]
    else:
        current = current[part]
if isinstance(current, (dict, list)):
    print(json.dumps(current))
else:
    print(current)
PY
}

json_find_approval_id() {
  local file="$1"
  local operation_type="$2"
  python3 - "$file" "$operation_type" <<'PY'
import json
import sys
from pathlib import Path

items = json.loads(Path(sys.argv[1]).read_text())
operation_type = sys.argv[2]
for item in items:
    if item.get("operation_type") == operation_type:
        print(item["id"])
        raise SystemExit(0)
raise SystemExit(1)
PY
}

json_find_workflow_status() {
  local file="$1"
  local run_id="$2"
  python3 - "$file" "$run_id" <<'PY'
import json
import sys
from pathlib import Path

runs = json.loads(Path(sys.argv[1]).read_text())
target_id = int(sys.argv[2])
for run in runs:
    if run.get("id") == target_id:
        print(run.get("status", ""))
        raise SystemExit(0)
raise SystemExit(1)
PY
}

json_len() {
  local file="$1"
  local path="$2"
  python3 - "$file" "$path" <<'PY'
import json
import sys
from pathlib import Path

obj = json.loads(Path(sys.argv[1]).read_text())
parts = sys.argv[2].split(".")
current = obj
for part in parts:
    if part == "":
        continue
    if part.isdigit():
        current = current[int(part)]
    else:
        current = current[part]
print(len(current))
PY
}

assert_file_nonempty() {
  local file_path="$1"
  if [[ ! -s "${file_path}" ]]; then
    echo "Expected non-empty artifact file: ${file_path}" >&2
    exit 1
  fi
}

check_page() {
  local name="$1"
  local path="$2"
  local expected_text="$3"
  local output="${OUT_DIR}/web_${name}.html"
  local status
  status="$(curl -sS -o "${output}" -w "%{http_code}" "${WEB_URL}${path}")"
  if [[ ! "${status}" =~ ^2 ]]; then
    echo "Frontend page failed: ${path} -> HTTP ${status}" >&2
    exit 1
  fi
  grep -q "LAEP Console" "${output}"
  grep -q "${expected_text}" "${output}"
}

if [[ ! -d "frontend/.next" ]]; then
  echo "Expected build output missing: frontend/.next" >&2
  exit 1
fi

api_call "01_health_live" "GET" "/api/v1/health/live"
api_call "02_health_ready" "GET" "/api/v1/health/ready"

api_call "03_auth_login_admin" "POST" "/api/v1/auth/login" \
  '{"username":"local-admin","password":"change-me-now"}'
ADMIN_TOKEN="$(json_get "${OUT_DIR}/03_auth_login_admin.json" "access_token")"
api_call "04_auth_me_admin" "GET" "/api/v1/auth/me" "" "${ADMIN_TOKEN}"

VIEWER_USER="viewer_live_${RUN_TS}"
VIEWER_EMAIL="${VIEWER_USER}@example.com"
VIEWER_PASS="Viewer-${RUN_TS}-Pass!"
api_call "05_auth_create_viewer" "POST" "/api/v1/auth/users" \
  "{\"email\":\"${VIEWER_EMAIL}\",\"username\":\"${VIEWER_USER}\",\"full_name\":\"Live Viewer\",\"password\":\"${VIEWER_PASS}\",\"role\":\"viewer\"}" \
  "${ADMIN_TOKEN}"
api_call "06_auth_login_viewer" "POST" "/api/v1/auth/login" \
  "{\"username\":\"${VIEWER_USER}\",\"password\":\"${VIEWER_PASS}\"}"
VIEWER_TOKEN="$(json_get "${OUT_DIR}/06_auth_login_viewer.json" "access_token")"
api_call "07_auth_me_viewer" "GET" "/api/v1/auth/me" "" "${VIEWER_TOKEN}"

api_expect_status "08_auth_viewer_create_user_forbidden" "POST" "/api/v1/auth/users" "403" \
  "{\"email\":\"blocked_${RUN_TS}@example.com\",\"username\":\"blocked_${RUN_TS}\",\"full_name\":\"Blocked\",\"password\":\"Blocked-${RUN_TS}-Pass!\",\"role\":\"viewer\"}" \
  "${VIEWER_TOKEN}"

api_call "10_agents_list" "GET" "/api/v1/agents/"
api_call "11_agents_execute_approval" "POST" "/api/v1/agents/execute" \
  '{"agent_name":"email","task":"compose","payload":{"subject":"Approve test","body":"Approval gate verification"},"context":{},"require_approval":true}' \
  "${ADMIN_TOKEN}"

api_call "12_email_summarize" "POST" "/api/v1/email/summarize" \
  '{"emails":[{"from":"ceo@example.com","subject":"Q3 plan","body":"Need board deck by Friday."},{"from":"ops@example.com","subject":"Incident report","body":"Root cause fixed; action items pending."}]}' \
  "${ADMIN_TOKEN}"
api_call "13_email_draft_reply" "POST" "/api/v1/email/draft-reply" \
  '{"email_thread":"Client asked for timeline and budget update.","tone":"professional"}' \
  "${ADMIN_TOKEN}"

api_call "14_calendar_conflicts" "POST" "/api/v1/calendar/conflicts" \
  '{"events":[{"title":"Ops","start":"2026-07-01T10:00:00Z","end":"2026-07-01T11:00:00Z","attendees":["ops@example.com"]},{"title":"Client Sync","start":"2026-07-01T10:30:00Z","end":"2026-07-01T11:15:00Z","attendees":["client@example.com"]}]}' \
  "${ADMIN_TOKEN}"
api_call "15_calendar_agenda" "POST" "/api/v1/calendar/agenda" \
  '{"context":"Weekly business review with finance, sales, and operations."}' \
  "${ADMIN_TOKEN}"

for value in 91 98 105 109 114; do
  api_call "20_analytics_metric_${value}" "POST" "/api/v1/analytics/metrics" \
    "{\"metric_name\":\"revenue_weekly\",\"metric_value\":${value},\"dimensions\":{\"region\":\"us\"}}" \
    "${ADMIN_TOKEN}"
done
api_call "21_analytics_summary" "GET" "/api/v1/analytics/metrics/revenue_weekly" "" "${ADMIN_TOKEN}"
ANALYTICS_AVG="$(json_get "${OUT_DIR}/21_analytics_summary.json" "average")"

api_call "30_report_create" "POST" "/api/v1/reports/" \
  "{\"name\":\"Weekly Revenue Summary ${RUN_TS}\",\"report_type\":\"weekly\",\"payload\":{\"title\":\"Weekly Revenue Summary\",\"average\":${ANALYTICS_AVG},\"sample_count\":5,\"insight\":\"Stable upward trend\"}}" \
  "${ADMIN_TOKEN}"
REPORT_ID="$(json_get "${OUT_DIR}/30_report_create.json" "id")"
api_call "31_report_export_pdf" "POST" "/api/v1/reports/${REPORT_ID}/export/pdf" "" "${ADMIN_TOKEN}"
api_call "32_report_export_xlsx" "POST" "/api/v1/reports/${REPORT_ID}/export/xlsx" "" "${ADMIN_TOKEN}"
api_call "33_report_export_pptx" "POST" "/api/v1/reports/${REPORT_ID}/export/pptx" "" "${ADMIN_TOKEN}"

REPORT_PDF="$(json_get "${OUT_DIR}/31_report_export_pdf.json" "path")"
REPORT_XLSX="$(json_get "${OUT_DIR}/32_report_export_xlsx.json" "path")"
REPORT_PPTX="$(json_get "${OUT_DIR}/33_report_export_pptx.json" "path")"
assert_file_nonempty "${REPORT_PDF}"
assert_file_nonempty "${REPORT_XLSX}"
assert_file_nonempty "${REPORT_PPTX}"

api_call "40_database_schemas" "GET" "/api/v1/database/schemas" "" "${ADMIN_TOKEN}"
api_call "41_database_users_preview" "GET" "/api/v1/database/tables/users?limit=10" "" "${ADMIN_TOKEN}"
api_call "42_database_query" "POST" "/api/v1/database/query?sql=SELECT%20id%2C%20username%2C%20role%20FROM%20users%20LIMIT%205" "" "${ADMIN_TOKEN}"

api_call "43_sql_generate" "POST" "/api/v1/sql/generate" \
  '{"prompt":"show the first 5 users with id and username","dialect":"sqlite","schema_hint":"users(id, username, role)"}' \
  "${ADMIN_TOKEN}"
api_call "44_sql_execute_select" "POST" "/api/v1/sql/execute" \
  '{"sql":"SELECT id, username, role FROM users LIMIT 5","confirm":false,"dry_run":false}' \
  "${ADMIN_TOKEN}"
api_call "45_sql_execute_destructive_requires_approval" "POST" "/api/v1/sql/execute" \
  '{"sql":"DELETE FROM users WHERE id = 1","confirm":false,"dry_run":false}' \
  "${ADMIN_TOKEN}"

api_call "50_dashboard_create" "POST" "/api/v1/dashboards/" \
  "{\"name\":\"Revenue Dashboard ${RUN_TS}\",\"definition\":{\"widgets\":[{\"type\":\"kpi\",\"name\":\"weekly_avg\",\"value\":${ANALYTICS_AVG}},{\"type\":\"report_link\",\"report_id\":${REPORT_ID}}]}}" \
  "${ADMIN_TOKEN}"
DASHBOARD_ID="$(json_get "${OUT_DIR}/50_dashboard_create.json" "id")"
api_call "51_dashboards_list" "GET" "/api/v1/dashboards/" "" "${ADMIN_TOKEN}"

api_call "52_memory_upsert" "POST" "/api/v1/memory/" \
  "{\"scope\":\"ops\",\"key\":\"last_report_id\",\"value\":{\"report_id\":${REPORT_ID},\"dashboard_id\":${DASHBOARD_ID}}}" \
  "${ADMIN_TOKEN}"
api_call "53_memory_list" "GET" "/api/v1/memory/" "" "${ADMIN_TOKEN}"

WORKFLOW_OPERATION="workflow_sensitive_followup_${RUN_TS}"
api_call "60_workflow_definition_create" "POST" "/api/v1/workflows/definitions" \
  "{\"name\":\"live_e2e_workflow_${RUN_TS}\",\"description\":\"Live verification workflow\",\"nodes\":[{\"id\":\"n1\",\"type\":\"condition\",\"config\":{\"expression\":\"True\"}},{\"id\":\"n2\",\"type\":\"approval\",\"config\":{\"operation_type\":\"${WORKFLOW_OPERATION}\",\"payload\":{\"action\":\"approve_followup\"}}},{\"id\":\"n3\",\"type\":\"notification\",\"config\":{\"message\":\"post-approval follow-up\"}}],\"edges\":[{\"source\":\"n1\",\"target\":\"n2\",\"condition\":\"context['n1']['decision'] == True\"},{\"source\":\"n2\",\"target\":\"n3\",\"condition\":null}],\"is_template\":false}" \
  "${ADMIN_TOKEN}"
WORKFLOW_DEFINITION_ID="$(json_get "${OUT_DIR}/60_workflow_definition_create.json" "id")"

api_call "61_workflow_run_start" "POST" "/api/v1/workflows/runs" \
  "{\"workflow_definition_id\":${WORKFLOW_DEFINITION_ID},\"context\":{\"source\":\"live_e2e\"}}" \
  "${ADMIN_TOKEN}"
WORKFLOW_RUN_ID="$(json_get "${OUT_DIR}/61_workflow_run_start.json" "id")"

WORKFLOW_STATUS=""
for _ in $(seq 1 20); do
  api_call "62_workflow_runs_list" "GET" "/api/v1/workflows/runs" "" "${ADMIN_TOKEN}"
  WORKFLOW_STATUS="$(json_find_workflow_status "${OUT_DIR}/62_workflow_runs_list.json" "${WORKFLOW_RUN_ID}" || true)"
  if [[ "${WORKFLOW_STATUS}" == "waiting_approval" ]]; then
    break
  fi
  sleep 1
done

if [[ "${WORKFLOW_STATUS}" != "waiting_approval" ]]; then
  echo "Workflow did not reach waiting_approval. Current status: ${WORKFLOW_STATUS}" >&2
  exit 1
fi

api_call "63_approvals_pending" "GET" "/api/v1/approvals/pending" "" "${ADMIN_TOKEN}"
WORKFLOW_APPROVAL_ID="$(json_find_approval_id "${OUT_DIR}/63_approvals_pending.json" "${WORKFLOW_OPERATION}")"
api_call "64_approval_decision" "POST" "/api/v1/approvals/${WORKFLOW_APPROVAL_ID}/decision" \
  '{"approve":true,"reason":"Approved during live verification"}' \
  "${ADMIN_TOKEN}"

api_call "70_notification_create" "POST" "/api/v1/notifications/" \
  "{\"channel\":\"in_app\",\"title\":\"Follow-up created\",\"body\":\"Report ${REPORT_ID} published and dashboard ${DASHBOARD_ID} updated.\",\"metadata\":{\"workflow_run_id\":${WORKFLOW_RUN_ID}}}" \
  "${ADMIN_TOKEN}"
FOLLOWUP_NOTIFICATION_ID="$(json_get "${OUT_DIR}/70_notification_create.json" "id")"
api_call "71_notifications_list" "GET" "/api/v1/notifications/" "" "${ADMIN_TOKEN}"

RUN_AT="$(python3 - <<'PY'
from datetime import UTC, datetime, timedelta
print((datetime.now(UTC) + timedelta(minutes=2)).isoformat())
PY
)"
api_call "72_scheduler_once" "POST" "/api/v1/scheduler/once" \
  "{\"run_at\":\"${RUN_AT}\",\"message\":\"live verification callback\"}" \
  "${ADMIN_TOKEN}"
api_call "73_scheduler_jobs" "GET" "/api/v1/scheduler/jobs" "" "${ADMIN_TOKEN}"

api_call "74_system_models" "GET" "/api/v1/system/models" "" "${ADMIN_TOKEN}"
api_call "75_system_monitoring" "GET" "/api/v1/system/monitoring" "" "${ADMIN_TOKEN}"

api_call "76_logs_audit_admin" "GET" "/api/v1/logs/audit" "" "${ADMIN_TOKEN}"
api_call "77_logs_audit_viewer" "GET" "/api/v1/logs/audit" "" "${VIEWER_TOKEN}"

api_call "78_agent_executions" "GET" "/api/v1/agents/executions" "" "${ADMIN_TOKEN}"

check_page "01_dashboard" "/" "Dashboard"
check_page "02_assistant" "/assistant" "AI Assistant"
check_page "03_email" "/email" "Email"
check_page "04_calendar" "/calendar" "Calendar"
check_page "05_reports" "/reports" "Reports"
check_page "06_analytics" "/analytics" "Analytics"
check_page "07_database" "/database" "Database Explorer"
check_page "08_sql" "/sql" "SQL Workspace"
check_page "09_workflows" "/workflows" "Workflow Builder"
check_page "10_documents" "/documents" "Documents"
check_page "11_knowledge" "/knowledge" "Knowledge Base"
check_page "12_memory" "/memory" "Memory"
check_page "13_agents" "/agents" "Agent Activity"
check_page "14_logs" "/logs" "Logs"
check_page "15_settings" "/settings" "Settings"
check_page "16_models" "/models" "Model Manager"
check_page "17_monitoring" "/monitoring" "System Monitoring"

if [[ "$(json_get "${OUT_DIR}/45_sql_execute_destructive_requires_approval.json" "safe")" != "False" ]]; then
  echo "SQL destructive safety gate did not trigger expected safe=false response." >&2
  exit 1
fi

if [[ "$(json_len "${OUT_DIR}/77_logs_audit_viewer.json" "")" != "0" ]]; then
  echo "Viewer audit log response is not empty; role restriction check failed." >&2
  exit 1
fi

INSTALLED_MODELS_COUNT="$(json_len "${OUT_DIR}/74_system_models.json" "installed_models")"
AUDIT_LOG_COUNT="$(json_len "${OUT_DIR}/76_logs_audit_admin.json" "")"

python3 - "$OUT_DIR/verification_summary.json" <<PY
import json
from pathlib import Path

summary = {
    "run_id": "${RUN_TS}",
    "out_dir": "${OUT_DIR}",
    "backend": "ok",
    "frontend": "ok",
    "admin_user": "local-admin",
    "viewer_user": "${VIEWER_USER}",
    "analytics_average": ${ANALYTICS_AVG},
    "report_id": int("${REPORT_ID}"),
    "dashboard_id": int("${DASHBOARD_ID}"),
    "workflow_run_id": int("${WORKFLOW_RUN_ID}"),
    "workflow_status": "${WORKFLOW_STATUS}",
    "workflow_approval_id": int("${WORKFLOW_APPROVAL_ID}"),
    "followup_notification_id": int("${FOLLOWUP_NOTIFICATION_ID}"),
    "report_artifacts": {
        "pdf": "${REPORT_PDF}",
        "xlsx": "${REPORT_XLSX}",
        "pptx": "${REPORT_PPTX}",
    },
    "installed_models_count": int("${INSTALLED_MODELS_COUNT}"),
    "audit_log_count_admin": int("${AUDIT_LOG_COUNT}"),
    "business_chain": "summarize_data -> generate_report -> update_dashboard -> create_followup_action",
}
Path("${OUT_DIR}/verification_summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
PY

echo "E2E verification completed: ${OUT_DIR}"
