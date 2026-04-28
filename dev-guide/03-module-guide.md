---
title: 模块开发指南
description: 添加任务类型、扩展指标、自定义模板、修改提醒逻辑、消息推送集成。
date: 2026-04-29
---

# 03 · 模块开发指南

## 添加新任务类型

### 步骤

1. 打开 `config.json`
2. 在 `task_types.types` 中添加新条目
3. 设置 emoji、label、keywords
4. 在 `task-tracker.sh` 的帮助信息中补充说明

### 模板

```json
{
  "deploy": {
    "emoji": "🚀",
    "label": "部署上线",
    "keywords": ["部署", "上线", "release", "deploy", "发布"]
  }
}
```

### 注册

在 `config.json` 的 `task_types.types` 中添加：

```json
"task_types": {
  "types": {
    "deploy": { "emoji": "🚀", "label": "部署上线", "keywords": [...] },
    ...
  }
}
```

报告生成器会自动识别新类型，无需修改代码。

## 添加新量化指标

### 步骤

1. 在 `task-tracker.sh` 中添加参数解析（`--新指标名`）
2. 在 `build_json()` 的 Python 代码中添加字段
3. 在 `report-generator.py` 的 `summarize()` 中累加
4. 在报告模板中添加输出行

### 模板（task-tracker.sh）

```bash
DEPLOY_COUNT=0
# ... 在参数解析 switch 中添加：
--deploy-count) DEPLOY_COUNT="$2"; shift 2 ;;
# ... 在 build_json 中添加：
'deploy_count': $DEPLOY_COUNT,
```

### 模板（report-generator.py）

```python
# summarize() 中：
totals["deploy_count"] += h.get("generate() 中：
totals["deploy_count"] += h.get("deploy_count", 0)

# generate_daily_report() 的表格中：
if totals["deploy_count"]:
    lines.append(f"| 部署次数 | {totals['deploy_count']} |")
```

## 自定义报告模板

报告模板在 `report-generator.py` 的 `generate_daily_report()`、`generate_brief()`、`generate_weekly_report()`、`generate_monthly_report()` 四个函数中。

### 修改精简版行数上限

```bash
python3 config-manager.py set report_style.brief_max_lines 20
```

### 修改任务类型显示顺序

在 `report-generator.py` 中修改 `type_order` 列表：

```python
type_order = ["requirement", "bugfix", "review", "tech", "doc", "meeting", "research", "other"]
```

## 修改提醒逻辑

提醒逻辑在 `task-tracker.sh` 末尾，通过 `notifier.sh` 推送：

```bash
# 当前逻辑：完成 N 个任务后通过 notifier.sh 推送提醒
if [[ "$MODE" == "count" && "$TOTAL" -eq "$THRESHOLD" ]]; then
  REMIND_MSG="💡 今日已完成 ${TOTAL} 个任务，可以说「日报」查看今日总结"
  bash "$SCRIPT_DIR/notifier.sh" -m "$REMIND_MSG" "${NOTIFIER_ARGS[@]}" 2>/dev/null || true
fi
```

### 扩展为 always 模式

```bash
if [[ "$MODE" == "always" ]]; then
  bash "$SCRIPT_DIR/notifier.sh" -m "📌 今日已完成 ${TOTAL} 个任务" "${NOTIFIER_ARGS[@]}" 2>/dev/null || true
elif [[ "$MODE" == "count" && "$TOTAL" -eq "$THRESHOLD" ]]; then
  bash "$SCRIPT_DIR/notifier.sh" -m "💡 可以查看日报了" "${NOTIFIER_ARGS[@]}" 2>/dev/null || true
fi
```

## 消息推送模块（notifier.sh）

### 架构

```
notifier.sh
    │
    ├── 读取 config.json → notification 配置
    ├── 检查 quiet_hours → 免打扰则跳过
    │
    ├── method=cli → openclaw message send
    │       └── 失败 → 降级到 webhook
    ├── method=webhook → curl POST /hooks/wake
    │       └── 失败 → 降级到 stdout
    └── method=none → 仅 stdout
```

### 添加新推送方式

1. 在 `notifier.sh` 的 `push_message()` case 中添加新分支
2. 在 `config.json` 的 `notification.method` 可选值中补充
3. 在 `config-manager.py` 的 `method_labels` 中补充显示

### 模板

```bash
# 在 push_message() 中添加：
new_method)
  if send_via_new_method; then
    return 0
  else
    echo "⚠️ 新方式失败，降级到 stdout" >&2
    echo "$MESSAGE"
    return 1
  fi
  ;;
```
