---
title: AI 日报自动生成系统
description: 完成任务自动打卡，说声「日报」就出报告。适配 OpenClaw / 大厂程序员 / 打工人工作流。
tags: [日报, 任务追踪, 自动化, 打工人]
date: 2026-04-29
---

# AI 日报自动生成系统

> 完成任务自动打卡，说声「日报」就出报告。

## 快速开始

```bash
# 1. 记录任务
bash task-tracker.sh -t requirement -n "写周报模板" --lines 15000

# 2. 查看日报
python3 report-generator.py --brief

# 3. 推送日报到聊天窗口
python3 report-generator.py --brief --send

# 4. 记录任务并推送提醒
bash task-tracker.sh -t requirement -n "写文档" --notify

# 5. 管理配置
python3 config-manager.py show
```

## 文件说明

| 文件 | 用途 |
|------|------|
| `config.json` | 配置中心（随时可调） |
| `config-manager.py` | 配置管理器（查看 / 修改 / 重置） |
| `task-tracker.sh` | 任务记录器（每完成任务调用） |
| `report-generator.py` | 日报 / 周报 / 月报生成器 |
| `notifier.sh` | 消息推送封装（CLI / Webhook / stdout） |
| `data/YYYY-MM-DD.jsonl` | 每日任务日志（自动创建） |
| `reports/YYYY-MM-DD.md` | 生成的报告文件 |
| `dev-guide/` | 开发手册（8 章） |
| `docs/` | 设计文档（方案设计书、集成方案） |

## 命令速查

### 记录任务

```bash
bash task-tracker.sh -t <类型> -n <名称> [选项]

# 类型: requirement | bugfix | review | tech | doc | meeting | research | other
bash task-tracker.sh -t requirement -n "用户详情页" --files 3 --lines 800
bash task-tracker.sh -t bugfix -n "修复购物车 Bug" --bugs 1
bash task-tracker.sh -t review -n "Review PR#456" --reviews 1

# 记录并推送提醒到聊天窗口
bash task-tracker.sh -t requirement -n "写文档" --notify
bash task-tracker.sh -t tech -n "重构" --notify --notify-channel telegram
```

### 生成报告

```bash
python3 report-generator.py              # 今日完整日报
python3 report-generator.py --brief      # 今日精简版
python3 report-generator.py --week       # 本周周报
python3 report-generator.py --month      # 本月月报
python3 report-generator.py --date 2026-04-28  # 指定日期

# 生成并推送到聊天窗口
python3 report-generator.py --brief --send
python3 report-generator.py --send --channel telegram --target @user
```

### 消息推送

```bash
bash notifier.sh -m "消息内容"                           # 默认方式推送
bash notifier.sh -m "消息内容" --channel telegram          # 指定渠道
bash notifier.sh -m "消息内容" --method none               # 仅 stdout
bash notifier.sh -m "消息内容" --dry-run                   # 测试模式
```

### 管理配置

```bash
python3 config-manager.py show                        # 查看配置
python3 config-manager.py set trigger.mode auto_count # 修改触发方式
python3 config-manager.py set report_style.mode full  # 修改推送格式
python3 config-manager.py reset                       # 重置默认
```

## 配置速览

所有选项通过 `config.json` + `config-manager.py` 管理：

| 配置项 | 可选值 | 默认值 |
|--------|--------|--------|
| `trigger.mode` | `manual` / `auto_count` / `auto_time` | `manual` |
| `report_style.mode` | `brief` / `full` / `both` | `brief` |
| `task_types.mode` | `preset_8` / `preset_4` / `custom` | `preset_8` |
| `reminder.mode` | `count` / `always` / `never` | `count` |
| `report_scope.mode` | `all` / `daily_only` / `daily_weekly` | `all` |
| `notification.method` | `cli` / `webhook` / `none` | `cli` |
| `notification.channel` | 渠道名 | 空（自动检测） |
| `notification.target` | 用户/频道 ID | 空（当前会话） |

## 开发手册

完整开发文档见 [`dev-guide/`](dev-guide/)，包含架构、环境搭建、模块开发、API 参考、测试、部署、排错、路线图共 8 章。

## 相关项目

- **Hermes Agent 版**：相同架构，指标体系针对 Hermes 工具链优化（Token / 工具调用 / 平台 / 技能）
