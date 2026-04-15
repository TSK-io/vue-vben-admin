#!/usr/bin/env bash

set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000/api/v1}"

json_field() {
  python3 - "$1" <<'PY'
import json
import sys

payload = json.loads(sys.stdin.read())
path = sys.argv[1].split(".")
value = payload
for part in path:
    if part.isdigit():
        value = value[int(part)]
    else:
        value = value[part]
print(value)
PY
}

api_post() {
  local path="$1"
  local body="$2"
  local token="${3:-}"
  if [[ -n "$token" ]]; then
    curl -fsS -H "Authorization: Bearer $token" -H 'Content-Type: application/json' -d "$body" "$BASE_URL$path"
  else
    curl -fsS -H 'Content-Type: application/json' -d "$body" "$BASE_URL$path"
  fi
}

api_get() {
  local path="$1"
  local token="${2:-}"
  if [[ -n "$token" ]]; then
    curl -fsS -H "Authorization: Bearer $token" "$BASE_URL$path"
  else
    curl -fsS "$BASE_URL$path"
  fi
}

login_token() {
  local username="$1"
  local password="$2"
  api_post "/auth/login" "{\"username\":\"$username\",\"password\":\"$password\"}" | json_field "data.access_token"
}

echo "[1/5] 检查服务健康与运行态"
api_get "/health" | json_field "data.status" >/dev/null
api_get "/health/runtime" | json_field "data.queue_strategy.max_concurrent_requests" >/dev/null

echo "[2/5] 验证老年端合规与求助链路"
elder_token="$(login_token "elder_demo" "111")"
api_post "/compliance/consents" '{"consent_type":"privacy_policy","policy_version":"2026.04"}' "$elder_token" | json_field "data.status" >/dev/null
api_get "/compliance/export" "$elder_token" | json_field "data.profile.display_name" >/dev/null
api_post "/elder/help-requests" '{"action_type":"联系家人","note":"脚本验收","notify_family":true,"notify_community":true}' "$elder_token" | json_field "data.help_id" >/dev/null

echo "[3/5] 验证子女端通知与隐私申请"
family_token="$(login_token "family_demo" "111")"
api_get "/notifications" "$family_token" | json_field "data.items.0.id" >/dev/null
api_post "/family/reminders" '{"elder_user_id":"u-elder-001","content":"先别转账，我马上联系你。","channel":"app"}' "$family_token" | json_field "data.notification_id" >/dev/null
api_post "/compliance/corrections" '{"field_name":"phone","new_value":"13900009999","reason":"号码变更"}' "$family_token" | json_field "data.request_type" >/dev/null
api_post "/compliance/deletions" '{"reason":"申请注销演示账号"}' "$family_token" | json_field "data.request_type" >/dev/null

echo "[4/5] 验证社区端工单与重点老人"
community_token="$(login_token "community_demo" "111")"
api_get "/community/elders" "$community_token" | json_field "data.items.0.elder_name" >/dev/null
api_post "/community/workorders/wo-001/transition" '{"action_type":"close","to_status":"closed","note":"脚本验收关闭工单","dispose_method":"phone_visit","dispose_result":"已完成核实"}' "$community_token" | json_field "data.status" >/dev/null

echo "[5/5] 验证管理端读取能力与审计"
admin_token="$(login_token "admin_demo" "111")"
api_get "/admin/rules" "$admin_token" | json_field "data.0.code" >/dev/null
api_get "/admin/system-config" "$admin_token" | json_field "data.0.key" >/dev/null
api_get "/compliance/audit-logs" "$family_token" | json_field "data.0.action" >/dev/null

echo "多角色联调验收通过"
