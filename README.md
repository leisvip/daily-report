---
title: AI 日报自动生成系统
description: 完成任务自动打卡，说声「日报」就出报告。
tags: [日报, 任务追踪, 自动化, 打工人]
date: 2026-04-29
---

<div align="center">

# 📋 AI 日报自动生成系统

**完成任务自动打卡，说声「日报」就出报告。**

[![Version](https://img.shields.io/badge/version-v1.1.0-blue?style=flat-square)](https://github.com/leisvip/daily-report/releases)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/leisvip/daily-report?style=social)](https://github.com/leisvip/daily-report/stargazers)

[快速开始](#-快速开始) · [功能特性](#-功能特性) · [命令速查](#-命令速查) · [开发手册](#-开发手册)

</div>

---

## ✨ 功能特性

| 特性 | 说明 |
|------|------|
| 🎯 **自动打卡** | 每完成一个任务自动记录到 JSONL 日志 |
| 📊 **多维报表** | 日报 / 周报 / 月报，精简版 + 完整版 |
| 🏷️ **8 种任务类型** | 需求、Bug、Review、技术建设、文档、会议、调研、其他 |
| 📡 **消息推送** | CLI → Webhook → stdout 三级降级，永远不丢数据 |
| 🔔 **智能提醒** | 完成 N 个任务后自动提示查看日报 |
| 🌙 **免打扰** | 23:00 - 08:00 静默，不打扰休息 |
| ⚙️ **全可配置** | 触发方式、推送格式、提醒规则，随时可调 |

## 🚀 快速开始

```bash
# 1. 记录任务
bash task-tracker.sh -t requirement -n "写周报模板" --lines 15000

# 2. 查看日报
python3 report-generator.py --brief

# 3. 推送到聊天窗口
python3 report-generator.py --brief --send

# 4. 记录并推送提醒
bash task-tracker.sh -t requirement -n "写文档" --notify

# 5. 管理配置
python3 config-manager.py show
```

## 📁 项目结构

```
daily-report/
├── task-tracker.sh          # 任务记录器
├── report-generator.py      # 日报 / 周报 / 月报生成器
├── notifier.sh              # 消息推送封装
├── config-manager.py        # 配置管理器
├── config.json              # 配置中心
├── data/                    # 每日任务日志（运行时生成）
│   └── YYYY-MM-DD.jsonl
├── reports/                 # 生成的报告文件（运行时生成）
│   └── YYYY-MM-DD.md
├── dev-guide/               # 开发手册（8 章）
└── docs/                    # 设计文档
```

## 📖 命令速查

### 记录任务

```bash
# 类型: requirement | bugfix | review | tech | doc | meeting | research | other
bash task-tracker.sh -t requirement -n "用户详情页" --files 3 --lines 800
bash task-tracker.sh -t bugfix -n "修复购物车 Bug" --bugs 1
bash task-tracker.sh -t review -n "Review PR#456" --reviews 1
```

### 生成报告

```bash
python3 report-generator.py              # 今日完整日报
python3 report-generator.py --brief      # 今日精简版
python3 report-generator.py --week       # 本周周报
python3 report-generator.py --month      # 本月月报
python3 report-generator.py --brief --send  # 生成并推送
```

### 消息推送

```bash
bash notifier.sh -m "消息内容"                      # 默认推送
bash notifier.sh -m "消息内容" --channel telegram    # 指定渠道
bash notifier.sh -m "消息内容" --dry-run             # 测试模式
```

### 管理配置

```bash
python3 config-manager.py show                        # 查看配置
python3 config-manager.py set trigger.mode auto_count # 修改触发方式
python3 config-manager.py set report_style.mode full  # 修改推送格式
python3 config-manager.py reset                       # 重置默认
```

## ⚙️ 配置速览

| 配置项 | 可选值 | 默认值 |
|--------|--------|--------|
| `trigger.mode` | `manual` / `auto_count` / `auto_time` | `manual` |
| `report_style.mode` | `brief` / `full` / `both` | `brief` |
| `task_types.mode` | `preset_8` / `preset_4` / `custom` | `preset_8` |
| `reminder.mode` | `count` / `always` / `never` | `count` |
| `notification.method` | `cli` / `webhook` / `none` | `cli` |

## 📚 开发手册

| 章节 | 内容 |
|------|------|
| [01-architecture](dev-guide/01-architecture.md) | 架构详解 · 数据流 · 设计决策 |
| [02-dev-setup](dev-guide/02-dev-setup.md) | 环境搭建 · 快速开始 |
| [03-module-guide](dev-guide/03-module-guide.md) | 模块开发 · 扩展指标 |
| [04-api-reference](dev-guide/04-api-reference.md) | CLI 参数 · 配置字段 · JSONL 格式 |
| [05-testing](dev-guide/05-testing.md) | 测试指南 · 验证流程 |
| [06-deployment](dev-guide/06-deployment.md) | 打包 · 部署 · 集成 |
| [07-troubleshooting](dev-guide/07-troubleshooting.md) | 常见问题 · 排错手册 |
| [08-roadmap](dev-guide/08-roadmap.md) | 路线图 · 功能规划 |

## 📄 License

[MIT](LICENSE)

---

<div align="center">

如果觉得有用，请给个 ⭐ Star 支持一下！

</div>
