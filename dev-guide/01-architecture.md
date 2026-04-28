---
title: 架构详解
description: 系统架构、数据流、模块依赖与设计决策。
date: 2026-04-29
---

# 01 · 架构详解

## 系统概览

```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层                             │
│                                                         │
│  聊天窗口（OpenClaw）    CLI 终端    配置管理器            │
└────────────────┬────────────────────────┬───────────────┘
                 │                        │
                 ▼                        ▼
┌────────────────────────┐    ┌────────────────────────┐
│   task-tracker.sh      │    │  config-manager.py     │
│   任务记录器            │    │  配置管理器             │
│                        │    │                        │
│  · 参数解析             │    │  · show / set / reset  │
│  · JSONL 追加写入       │    │  · 类型自动转换         │
│  · 提醒阈值检查         │    │  · 导入 / 导出         │
│  · 调用 notifier 推送   │    │  · notification 管理   │
└───────────┬────────────┘    └────────────────────────┘
            │
            ▼
┌────────────────────────┐    ┌────────────────────────┐
│  data/YYYY-MM-DD.jsonl │    │  config.json           │
│  每日任务日志            │    │  配置中心               │
│                        │    │                        │
│  · 一行一条 JSON        │    │  · 触发方式             │
│  · 追加写入，不覆盖      │    │  · 推送格式             │
│  · 按日期自动分文件      │    │  · 任务类型             │
└───────────┬────────────┘    │  · 提醒规则             │
            │                 │  · 报告范围             │
            ▼                 │  · 消息推送             │
┌────────────────────────┐    └────────────────────────┘
│  report-generator.py   │
│  日报 / 周报 / 月报     │
│                        │
│  · 读取 JSONL           │
│  · 按类型分类汇总        │
│  · 套用模板渲染          │
│  · 输出精简版 / 完整版   │
│  · 调用 notifier 推送   │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐    ┌────────────────────────┐
│  reports/YYYY-MM-DD.md │    │  notifier.sh           │
│  生成的报告文件          │    │  消息推送封装           │
│                        │    │                        │
└────────────────────────┘    │  · CLI 推送（主）       │
                              │  · Webhook 降级         │
                              │  · stdout 保底          │
                              │  · 免打扰检查           │
                              └───────────┬────────────┘
                                          │
                                          ▼
                              ┌────────────────────────┐
                              │  OpenClaw 消息渠道      │
                              │  Telegram/Discord/...   │
                              └────────────────────────┘
```

## 数据流

```
任务完成
   │
   ├──→ task-tracker.sh -t <类型> -n <名称> [--notify] [指标]
   │         │
   │         ├──→ data/2026-04-29.jsonl   ← 追加一行 JSON
   │         │
   │         └──→ notifier.sh             ← --notify 时推送确认
   │                   │
   │                   ├── openclaw message send（CLI 推送）
   │                   └── stdout（双写保底）
   │
   ▼
用户说「日报」
   │
   ├──→ report-generator.py --brief --send   ← 精简版 + 推送
   │         │
   │         ├──→ 聊天窗口显示（notifier.sh 推送）
   │         └──→ stdout（双写保底）
   │
   └──→ report-generator.py --save           ← 完整版保存
             │
             ▼
        reports/2026-04-29.md
```

## 模块依赖

```
config.json  （无依赖 — 所有模块读取此文件）
     ↑
task-tracker.sh  （读取 config → 提醒阈值；调用 notifier → 推送）
report-generator.py  （读取 config → 类型/格式/范围；调用 notifier → 推送）
config-manager.py  （读写 config → show/set/reset/notification 管理）
notifier.sh  （读取 config → notification 配置；调用 openclaw CLI → 消息推送）
     ↑
data/*.jsonl  （task-tracker 写入，report-generator 读取）
reports/*.md  （report-generator 写入）
```

## 关键设计决策

| 决策 | 选择 | 原因 |
|------|------|------|
| 任务记录 | Shell 脚本 | 零依赖，一行命令完成 |
| 报告生成 | Python | JSON 处理和模板渲染能力强 |
| 存储格式 | JSONL | 追加写入友好，每行独立可解析 |
| 配置格式 | JSON | Python 原生支持，可读性好 |
| 报告格式 | Markdown | 通用、可渲染、易阅读 |
| 触发方式 | 配置化 | 用户随时可调，不改代码 |
| 消息推送 | notifier.sh 封装 | 统一入口，CLI/Webhook/stdout 三级降级 |
| 推送默认 | 关闭（需 --send/--notify） | 不主动打扰用户 |
| 推送双写 | 推送 + stdout | 保底不丢数据 |
