#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  task-tracker.sh — 任务记录器
#  每完成一个任务调用一次，追加写入当日 JSONL 日志
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/config.json"

# ── 读取配置 ──
DATA_DIR=$(python3 -c "import json,os; c=json.load(open('$CONFIG')); print(os.path.join('$SCRIPT_DIR', c['general']['data_dir']))")
mkdir -p "$DATA_DIR"

# ── 当前时间 ──
now_ts() { date +"%Y-%m-%dT%H:%M:%S%z"; }
today()  { date +"%Y-%m-%d"; }
log_file() { echo "$DATA_DIR/$(today).jsonl"; }

# ── 参数解析 ──
TYPE="other"
NAME=""
DESC=""
LINES=0
FILES=0
COMMITS=0
BUGS=0
REVIEWS=0
DURATION=0
STATUS="done"
TAGS=""
FILES_CHANGED=""
NOTIFY=false
NOTIFY_CHANNEL=""
NOTIFY_TARGET=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -t|--type)        TYPE="$2"; shift 2 ;;
    -n|--name)        NAME="$2"; shift 2 ;;
    -d|--desc)        DESC="$2"; shift 2 ;;
    --lines)          LINES="$2"; shift 2 ;;
    --files)          FILES="$2"; shift 2 ;;
    --commits)        COMMITS="$2"; shift 2 ;;
    --bugs)           BUGS="$2"; shift 2 ;;
    --reviews)        REVIEWS="$2"; shift 2 ;;
    --duration)       DURATION="$2"; shift 2 ;;
    --status)         STATUS="$2"; shift 2 ;;
    --tags)           TAGS="$2"; shift 2 ;;
    --files-changed)  FILES_CHANGED="$2"; shift 2 ;;
    --notify)         NOTIFY=true; shift ;;
    --notify-channel) NOTIFY_CHANNEL="$2"; shift 2 ;;
    --notify-target)  NOTIFY_TARGET="$2"; shift 2 ;;
    -h|--help)
      echo "用法: task-tracker.sh -t <类型> -n <名称> [选项]"
      echo ""
      echo "必填:"
      echo "  -t, --type <类型>       任务类型: requirement|bugfix|review|tech|doc|meeting|research|other"
      echo "  -n, --name <名称>       任务名称（一句话）"
      echo ""
      echo "可选:"
      echo "  -d, --desc <描述>       任务详细描述"
      echo "  --lines <n>             代码/文档行数"
      echo "  --files <n>             涉及文件数"
      echo "  --commits <n>           Git commit 数"
      echo "  --bugs <n>              修复 Bug 数"
      echo "  --reviews <n>           Review 次数"
      echo "  --duration <分钟>       耗时"
      echo "  --status <状态>         done|wip|blocked（默认 done）"
      echo "  --tags <标签>           逗号分隔的标签"
      echo "  --files-changed <路径>  关联文件路径"
      echo "  --notify                推送提醒到聊天窗口"
      echo "  --notify-channel <渠道> 指定推送渠道"
      echo "  --notify-target <目标>  指定推送目标"
      exit 0 ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

if [[ -z "$NAME" ]]; then
  echo "❌ 缺少任务名称 (-n)"
  exit 1
fi

# ── 构建 tags JSON 数组 ──
if [[ -n "$TAGS" ]]; then
  TAGS_JSON=$(echo "$TAGS" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip().split(',')))")
else
  TAGS_JSON="[]"
fi

# ── 构建 files_changed JSON 数组 ──
if [[ -n "$FILES_CHANGED" ]]; then
  FC_JSON=$(echo "$FILES_CHANGED" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip().split(',')))")
else
  FC_JSON="[]"
fi

# ── 写入 JSONL ──
ENTRY=$(TASK_NAME="$NAME" TASK_DESC="$DESC" TASK_TYPE="$TYPE" TASK_STATUS="$STATUS" \
  TASK_TS="$(now_ts)" TASK_LINES="$LINES" TASK_FILES="$FILES" TASK_COMMITS="$COMMITS" \
  TASK_BUGS="$BUGS" TASK_REVIEWS="$REVIEWS" TASK_DURATION="$DURATION" \
  python3 -c "
import json, os
entry = {
    'ts': os.environ['TASK_TS'],
    'type': os.environ['TASK_TYPE'],
    'name': os.environ['TASK_NAME'],
    'desc': os.environ['TASK_DESC'],
    'metrics': {
        'lines': int(os.environ['TASK_LINES']),
        'files': int(os.environ['TASK_FILES']),
        'commits': int(os.environ['TASK_COMMITS']),
        'bugs': int(os.environ['TASK_BUGS']),
        'reviews': int(os.environ['TASK_REVIEWS']),
        'duration_min': int(os.environ['TASK_DURATION'])
    },
    'status': os.environ['TASK_STATUS'],
    'tags': $(echo "$TAGS_JSON"),
    'files_changed': $(echo "$FC_JSON")
}
print(json.dumps(entry, ensure_ascii=False))
")

echo "$ENTRY" >> "$(log_file)"

# ── 返回统计 ──
TOTAL=$(wc -l < "$(log_file)" | tr -d ' ')
echo "✅ 任务已记录 [$TYPE] $NAME"
echo "   📊 今日已完成: ${TOTAL} 个任务"
echo "   📁 日志: $(log_file)"

# ── 构建 notifier 推送参数 ──
NOTIFIER_ARGS=()
if [[ -n "$NOTIFY_CHANNEL" ]]; then
  NOTIFIER_ARGS+=(--channel "$NOTIFY_CHANNEL")
fi
if [[ -n "$NOTIFY_TARGET" ]]; then
  NOTIFIER_ARGS+=(--target "$NOTIFY_TARGET")
fi

# ── 显式 --notify 推送任务记录确认 ──
if $NOTIFY; then
  NOTIFY_MSG="✅ 任务已记录 [$TYPE] $NAME
📊 今日已完成: ${TOTAL} 个任务"
  bash "$SCRIPT_DIR/notifier.sh" -m "$NOTIFY_MSG" "${NOTIFIER_ARGS[@]}" 2>/dev/null || true
fi

# ── 检查是否需要提醒（达到阈值时自动推送，不受 --notify 控制） ──
MODE=$(python3 -c "import json; c=json.load(open('$CONFIG')); print(c['reminder']['mode'])")
THRESHOLD=$(python3 -c "import json; c=json.load(open('$CONFIG')); print(c['reminder']['count_threshold'])")

if [[ "$MODE" == "count" && "$TOTAL" -eq "$THRESHOLD" ]]; then
  REMIND_MSG="💡 今日已完成 ${TOTAL} 个任务，可以说「日报」查看今日总结"
  echo ""
  echo "$REMIND_MSG"
  bash "$SCRIPT_DIR/notifier.sh" -m "$REMIND_MSG" "${NOTIFIER_ARGS[@]}" 2>/dev/null || true
fi
