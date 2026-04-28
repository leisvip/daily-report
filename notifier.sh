#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  notifier.sh — OpenClaw 消息推送封装
#  统一入口：CLI 推送 → Webhook 降级 → stdout 保底
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/config.json"

# ── 参数解析 ──
MESSAGE=""
CHANNEL=""
TARGET=""
METHOD=""        # cli | webhook | none（空=读配置）
DRY_RUN=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    -m|--message)   MESSAGE="$2"; shift 2 ;;
    --channel)      CHANNEL="$2"; shift 2 ;;
    --target)       TARGET="$2"; shift 2 ;;
    --method)       METHOD="$2"; shift 2 ;;
    --dry-run)      DRY_RUN=true; shift ;;
    --verbose)      VERBOSE=true; shift ;;
    -h|--help)
      echo "用法: notifier.sh -m <消息内容> [选项]"
      echo ""
      echo "必填:"
      echo "  -m, --message <text>    要推送的消息内容"
      echo ""
      echo "可选:"
      echo "  --channel <渠道>        聊天渠道 (telegram|discord|whatsapp|...)"
      echo "  --target <目标>         推送目标 (用户ID/chatID/@username)"
      echo "  --method <方式>         推送方式 (cli|webhook|none)"
      echo "  --dry-run               仅打印，不实际推送"
      echo "  --verbose               详细日志"
      exit 0 ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

if [[ -z "$MESSAGE" ]]; then
  echo "❌ 缺少消息内容 (-m)"
  exit 1
fi

# ── 读取配置 ──
load_cfg() {
  python3 -c "
import json, sys
try:
    c = json.load(open('$CONFIG'))
    notif = c.get('notification', {})
    method = notif.get('method', 'cli')
    channel = notif.get('channel', '')
    target = notif.get('target', '')
    wh = notif.get('webhook', {})
    wh_url = wh.get('url', 'http://127.0.0.1:18789/hooks/wake')
    wh_token = wh.get('token', '')
    quiet = notif.get('quiet_hours', {})
    quiet_enabled = quiet.get('enabled', False)
    quiet_start = quiet.get('start', '23:00')
    quiet_end = quiet.get('end', '08:00')
    print(f'{method}|{channel}|{target}|{wh_url}|{wh_token}|{quiet_enabled}|{quiet_start}|{quiet_end}')
except Exception as e:
    print(f'cli|||||||', file=sys.stderr)
    print('cli|||||||')
"
}

CFG_LINE=$(load_cfg)
IFS='|' read -r CFG_METHOD CFG_CHANNEL CFG_TARGET WH_URL WH_TOKEN QUIET_ENABLED QUIET_START QUIET_END <<< "$CFG_LINE"

# 合并：命令行 > 配置文件
FINAL_METHOD="${METHOD:-$CFG_METHOD}"
FINAL_CHANNEL="${CHANNEL:-$CFG_CHANNEL}"
FINAL_TARGET="${TARGET:-$CFG_TARGET}"

# ── 免打扰检查 ──
is_quiet_hours() {
  if [[ "$QUIET_ENABLED" != "True" && "$QUIET_ENABLED" != "true" ]]; then
    return 1
  fi
  local now_h now_m start_h start_m end_h end_m
  now_h=$(date +%H | sed 's/^0//')
  now_m=$(date +%M | sed 's/^0//')
  start_h=$(echo "$QUIET_START" | cut -d: -f1 | sed 's/^0//')
  start_m=$(echo "$QUIET_START" | cut -d: -f2 | sed 's/^0//')
  end_h=$(echo "$QUIET_END" | cut -d: -f1 | sed 's/^0//')
  end_m=$(echo "$QUIET_END" | cut -d: -f2 | sed 's/^0//')

  local now_total=$((now_h * 60 + now_m))
  local start_total=$((start_h * 60 + start_m))
  local end_total=$((end_h * 60 + end_m))

  if [[ $start_total -le $end_total ]]; then
    # 同一天内（如 08:00 - 23:00）
    [[ $now_total -ge $start_total && $now_total -le $end_total ]] && return 0 || return 1
  else
    # 跨午夜（如 23:00 - 08:00）
    [[ $now_total -ge $start_total || $now_total -le $end_total ]] && return 0 || return 1
  fi
}

if is_quiet_hours; then
  if $VERBOSE; then
    echo "🌙 免打扰时段 ($QUIET_START - $QUIET_END)，跳过推送"
  fi
  # 免打扰时仍打印到 stdout（双写保底）
  echo "$MESSAGE"
  exit 0
fi

# ── 推送函数 ──
send_via_cli() {
  local cmd="openclaw message send --message"
  local args=()

  # 需要用 printf 处理转义，避免 echo 的 -e 问题
  args+=(--message "$MESSAGE")

  if [[ -n "$FINAL_CHANNEL" ]]; then
    args+=(--channel "$FINAL_CHANNEL")
  fi
  if [[ -n "$FINAL_TARGET" ]]; then
    args+=(--target "$FINAL_TARGET")
  fi
  if $DRY_RUN; then
    args+=(--dry-run)
  fi
  if $VERBOSE; then
    args+=(--verbose)
  fi

  if $VERBOSE; then
    echo "📡 CLI 推送: openclaw message send ${args[*]}"
  fi

  openclaw message send "${args[@]}" 2>&1
}

send_via_webhook() {
  if [[ -z "$WH_URL" ]]; then
    echo "❌ Webhook URL 未配置"
    return 1
  fi

  # 构建 JSON payload
  local payload
  payload=$(python3 -c "
import json, sys
msg = sys.argv[1]
print(json.dumps({'text': msg, 'mode': 'now'}))
" "$MESSAGE")

  local curl_args=(-s -w '\n%{http_code}')
  curl_args+=(-X POST "$WH_URL")
  curl_args+=(-H 'Content-Type: application/json')

  if [[ -n "$WH_TOKEN" ]]; then
    curl_args+=(-H "Authorization: Bearer $WH_TOKEN")
  fi

  curl_args+=(-d "$payload")
  curl_args+=(--connect-timeout 10 --max-time 15)

  if $VERBOSE; then
    echo "📡 Webhook 推送: curl ${curl_args[*]}"
  fi

  if $DRY_RUN; then
    echo "[DRY-RUN] Webhook: $WH_URL"
    echo "[DRY-RUN] Payload: $payload"
    return 0
  fi

  local response
  response=$(curl "${curl_args[@]}" 2>&1) || true
  local http_code
  http_code=$(echo "$response" | tail -1)
  local body
  body=$(echo "$response" | sed '$d')

  if [[ "$http_code" =~ ^2 ]]; then
    if $VERBOSE; then
      echo "✅ Webhook 推送成功 (HTTP $http_code)"
    fi
    return 0
  else
    echo "⚠️ Webhook 推送失败 (HTTP $http_code): $body"
    return 1
  fi
}

# ── 主推送逻辑 ──
push_message() {
  case "$FINAL_METHOD" in
    cli)
      if send_via_cli; then
        return 0
      else
        echo "⚠️ CLI 推送失败，尝试 Webhook 降级..." >&2
        if send_via_webhook; then
          return 0
        else
          echo "⚠️ Webhook 也失败，降级到 stdout" >&2
          echo "$MESSAGE"
          return 1
        fi
      fi
      ;;
    webhook)
      if send_via_webhook; then
        return 0
      else
        echo "⚠️ Webhook 推送失败，降级到 stdout" >&2
        echo "$MESSAGE"
        return 1
      fi
      ;;
    none)
      if $VERBOSE; then
        echo "🔇 推送已关闭 (method=none)"
      fi
      echo "$MESSAGE"
      return 0
      ;;
    *)
      echo "⚠️ 未知推送方式: $FINAL_METHOD，降级到 stdout" >&2
      echo "$MESSAGE"
      return 1
      ;;
  esac
}

# ── 双写：推送 + stdout ──
echo "$MESSAGE"
push_message
