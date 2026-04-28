---
title: API 与 CLI 参考
description: 所有命令行参数、配置字段、JSONL 数据格式。
date: 2026-04-29
---

# 04 · API 与 CLI 参考

## task-tracker.sh 参数

| 参数 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `-t, --type` | 是 | string | 任务类型 |
| `-n, --name` | 是 | string | 任务名称 |
| `-d, --desc` | 否 | string | 任务描述 |
| `--lines` | 否 | int | 代码 / 文档行数 |
| `--files` | 否 | int | 涉及文件数 |
| `--commits` | 否 | int | Git commit 数 |
| `--bugs` | 否 | int | 修复 Bug 数 |
| `--reviews` | 否 | int | Review 次数 |
| `--duration` | 否 | int | 耗时（分钟） |
| `--status` | 否 | string | `done` / `wip` / `blocked` |
| `--tags` | 否 | string | 逗号分隔标签 |
| `--files-changed` | 否 | string | 关联文件路径 |
| `--notify` | 否 | flag | 推送任务记录确认到聊天窗口 |
| `--notify-channel` | 否 | string | 指定推送渠道 |
| `--notify-target` | 否 | string | 指定推送目标 |

## report-generator.py 参数

| 参数 | 说明 |
|------|------|
| `--date YYYY-MM-DD` | 指定日期（默认今天） |
| `--brief` | 精简版输出 |
| `--week` | 生成周报 |
| `--month` | 生成月报 |
| `--save` | 保存到文件（默认开启） |
| `--no-save` | 不保存文件 |
| `--send` | 推送到聊天窗口 |
| `--channel` | 推送渠道 (telegram\|discord\|whatsapp\|...) |
| `--target` | 推送目标 (用户ID/chatID/@username) |

## notifier.sh 参数

| 参数 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `-m, --message` | 是 | string | 要推送的消息内容 |
| `--channel` | 否 | string | 聊天渠道 |
| `--target` | 否 | string | 推送目标 |
| `--method` | 否 | string | 推送方式 (cli\|webhook\|none) |
| `--dry-run` | 否 | flag | 仅打印，不实际推送 |
| `--verbose` | 否 | flag | 详细日志 |

## config-manager.py 命令

| 命令 | 说明 |
|------|------|
| `show` | 显示当前配置 |
| `set <key> <value>` | 修改配置项 |
| `reset` | 重置为默认 |
| `export` | 导出 JSON |
| `import '<json>'` | 导入配置 |

## config.json 配置字段

| 路径 | 类型 | 可选值 | 说明 |
|------|------|--------|------|
| `trigger.mode` | string | `manual` / `auto_count` / `auto_time` | 触发方式 |
| `trigger.auto_count_threshold` | int | 1-100 | 计数触发阈值 |
| `trigger.auto_time_hour` | int | 0-23 | 定时触发小时 |
| `trigger.auto_time_minute` | int | 0-59 | 定时触发分钟 |
| `report_style.mode` | string | `brief` / `full` / `both` | 推送格式 |
| `report_style.brief_max_lines` | int | 5-50 | 精简版最大行数 |
| `task_types.mode` | string | `preset_8` / `preset_4` / `custom` | 类型模式 |
| `reminder.mode` | string | `count` / `always` / `never` | 提醒模式 |
| `reminder.count_threshold` | int | 1-100 | 计数提醒阈值 |
| `reminder.quiet_hours.enabled` | bool | `true` / `false` | 免打扰开关 |
| `report_scope.mode` | string | `all` / `daily_only` / `daily_weekly` | 报告范围 |
| `notification.method` | string | `cli` / `webhook` / `none` | 推送方式 |
| `notification.channel` | string | 渠道名 | 推送渠道 |
| `notification.target` | string | 用户/频道 ID | 推送目标 |
| `notification.webhook.url` | string | URL | Webhook 端点 |
| `notification.webhook.token` | string | secret | 认证 token |
| `notification.quiet_hours.enabled` | bool | `true` / `false` | 免打扰开关 |

## JSONL 数据格式

每行一条 JSON，字段如下：

```json
{
  "ts": "2026-04-29T02:25:00+0800",
  "type": "requirement",
  "name": "编写周报模板",
  "desc": "编写 15000 字的模板大全",
  "metrics": {
    "lines": 15000,
    "files": 1,
    "commits": 0,
    "bugs": 0,
    "reviews": 0,
    "duration_min": 0
  },
  "status": "done",
  "tags": ["文档", "写作"],
  "files_changed": []
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `ts` | string | ISO 8601 时间戳 |
| `type` | string | 任务类型 |
| `name` | string | 任务名称 |
| `desc` | string | 任务描述 |
| `metrics` | object | 量化指标 |
| `status` | string | `done` / `wip` / `blocked` |
| `tags` | array | 标签列表 |
| `files_changed` | array | 关联文件 |
