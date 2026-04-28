---
title: AI 日报自动生成系统 · 开发手册
description: 基于 OpenClaw 的任务追踪与日报/周报/月报自动生成系统，适配程序员工作流。
tags: [日报, 打工人, 任务追踪, 自动化]
date: 2026-04-29
---

# AI 日报自动生成系统 · 开发手册

> 完成任务自动打卡，说声「日报」就出报告。适配 OpenClaw / 大厂程序员 / 打工人工作流。

## 项目关系

```
┌──────────────────┐         ┌──────────────────┐
│  OpenClaw 版      │  同构    │  Hermes Agent 版  │
│  daily-report/    │ ◄─────► │  hermes-daily-    │
│                   │         │  report/          │
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         ▼                            ▼
┌──────────────────────────────────────────────┐
│              config.json 配置中心              │
│  触发方式 · 推送格式 · 任务类型 · 提醒规则      │
└──────────────────────────────────────────────┘
```

## 目录

| 文件 | 内容 |
|------|------|
| [01-architecture](01-architecture.md) | 架构详解 · 数据流 · 设计决策 |
| [02-dev-setup](02-dev-setup.md) | 环境搭建 · 快速开始 · 命令速查 |
| [03-module-guide](03-module-guide.md) | 模块开发指南 · 添加任务类型 · 扩展指标 |
| [04-api-reference](04-api-reference.md) | CLI 命令 · 配置字段 · JSONL 格式 |
| [05-testing](05-testing.md) | 测试指南 · 验证流程 |
| [06-deployment](06-deployment.md) | 打包 · 部署 · 与 Hermes 集成 |
| [07-troubleshooting](07-troubleshooting.md) | 常见问题 · 排错手册 |
| [08-roadmap](08-roadmap.md) | 后续路线图 · 功能规划 |

## 快速体验

```bash
# 记录任务
bash task-tracker.sh -t requirement -n "写周报模板" --lines 15000

# 查看日报
python3 report-generator.py --brief

# 管理配置
python3 config-manager.py show
```
