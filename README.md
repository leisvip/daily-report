---
title: 赛博牛马日报
description: 完成任务自动打卡，说声「日报」就出报告。OpenClaw 专属，零基础可用。
tags: [日报, 任务追踪, 自动化, 打工人, OpenClaw]
date: 2026-04-29
---

<div align="center">

# 📋 赛博牛马日报

**完成任务自动打卡，说声「日报」就出报告。**

**你不需要会 git，不需要会 Python，甚至不需要打开终端。**
**你只需要会说人话。**

[![Version](https://img.shields.io/badge/version-v1.1.0-blue?style=flat-square)](https://github.com/leisvip/daily-report/releases)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/leisvip/daily-report?style=social)](https://github.com/leisvip/daily-report/stargazers)

[我是小白，怎么用？](#-小白指南动嘴就行) · [我懂技术，命令呢？](#-命令速查) · [这玩意儿怎么工作的？](#-架构一览)

</div>

---

## 🐴 这是什么？

**赛博牛马日报**是一个给 AI 助手（比如 OpenClaw）用的「自动记工时 + 出日报」系统。

**类比：** 你去上班，每天干了什么活，月底要写日报。以前你得自己回忆、自己写。现在你的 AI 助手帮你记、帮你写、还帮你发到聊天窗口。

**它怎么做到的？**

```
你：帮我写个文档
AI：写好了！（顺便在后台记了一笔：「写文档 ✅」）
你：日报
AI：今日完成 3 个任务：写文档、改 Bug、Review 代码...
```

就这么简单。

---

## 🐣 小白指南：动嘴就行

### 第一步：跟 OpenClaw 说句话

打开你和 OpenClaw 的对话窗口（Telegram / Discord / Web 都行），然后说：

```
帮我记录一个任务：写周报，类型是需求开发，代码 500 行
```

OpenClaw 会自动：
1. 调用 `task-tracker.sh` 记录任务
2. 追加到当天的日志文件（`data/2026-04-29.jsonl`）
3. 告诉你「记好了，今天已完成 1 个任务」

**你不需要知道 `task-tracker.sh` 是什么，不需要知道 JSONL 是什么，不需要知道文件在哪。** 你只需要说人话。

### 第二步：查看日报

干完活了，想看看今天干了啥？说：

```
日报
```

或者：

```
今日总结
```

OpenClaw 会自动：
1. 调用 `report-generator.py --brief`
2. 读取今天的任务日志
3. 按类型分类汇总
4. 生成精简版日报
5. 直接发到你的聊天窗口

**你就说了一句「日报」，它帮你干了五件事。**

### 第三步：推送到指定渠道

想把日报发到 Telegram 群？Discord 频道？WhatsApp？

```
把日报发到 Telegram
```

OpenClaw 会自动：
1. 生成日报内容
2. 调用 `notifier.sh`
3. 通过 `openclaw message send` 推送到 Telegram

**推送链路：** `脚本 → notifier.sh → openclaw message send → Telegram / Discord / WhatsApp`

你不需要配置任何东西，OpenClaw 已经帮你接好了。

### 第四步：查看周报 / 月报

```
周报
```

```
月报
```

OpenClaw 会自动汇总本周 / 本月的所有任务数据，生成对应报告。

### 第五步：改配置

想改提醒规则？改推送格式？

```
把提醒改成每个任务都提醒
```

```
日报用完整版格式
```

OpenClaw 会调用 `config-manager.py` 修改配置，你不需要打开任何文件。

---

## 🎯 你可以说的话（OpenClaw 指令映射）

| 你说 | OpenClaw 做 |
|------|-------------|
| "记录任务：写文档" | 调用 `task-tracker.sh -t other -n "写文档"` |
| "记录需求：用户详情页，800 行" | 调用 `task-tracker.sh -t requirement -n "用户详情页" --lines 800` |
| "记录 Bug：修复购物车" | 调用 `task-tracker.sh -t bugfix -n "修复购物车"` |
| "日报" | 调用 `report-generator.py --brief` |
| "完整日报" | 调用 `report-generator.py`（无 --brief） |
| "周报" | 调用 `report-generator.py --week` |
| "月报" | 调用 `report-generator.py --month` |
| "发到 Telegram" | 调用 `report-generator.py --brief --send --channel telegram` |
| "查看配置" | 调用 `config-manager.py show` |
| "改提醒模式" | 调用 `config-manager.py set reminder.mode <值>` |
| "今天干了几件事？" | 读取日志文件，统计行数 |

**全程零命令行，零文件操作，零 git 操作。** 你只需要说人话。

---

## 🧠 架构一览

> 以下内容给想了解原理的人看。**小白可以跳过。**

### 数据流

```
你说话 → OpenClaw 理解意图 → 调用脚本 → 写入日志 → 生成报告 → 推送到聊天窗口
```

### 文件结构

```
daily-report/
├── task-tracker.sh          # 任务记录器（每完成任务调用一次）
├── report-generator.py      # 日报 / 周报 / 月报生成器
├── notifier.sh              # 消息推送封装
│                            #   ↓ 优先级
│                            #   1. openclaw message send（本地 CLI）
│                            #   2. Webhook API（远程场景）
│                            #   3. stdout 打印（保底不丢）
├── config-manager.py        # 配置管理器（查看 / 修改 / 重置）
├── config.json              # 配置中心（所有选项都在这）
├── data/                    # 每日任务日志（运行时自动创建）
│   └── 2026-04-29.jsonl     #   一行一条 JSON，追加写入
├── reports/                 # 生成的报告文件（运行时自动创建）
│   └── 2026-04-29.md
├── dev-guide/               # 开发手册（8 章，给开发者看）
└── docs/                    # 设计文档（方案设计书、集成方案）
```

### 推送链路

```
report-generator.py --send
    │
    ├── 生成报告内容
    │
    └── 调用 notifier.sh -m "报告内容"
            │
            ├── 方法 1：openclaw message send（最常用）
            │       └── 直接推送到 Telegram / Discord / WhatsApp
            │
            ├── 方法 2：Webhook API（降级）
            │       └── curl POST 到 /hooks/wake
            │
            └── 方法 3：stdout 打印（保底）
                    └── 永远不丢数据
```

### 任务类型

| 类型 | Emoji | 说明 |
|------|-------|------|
| `requirement` | 🔴 | 需求开发 |
| `bugfix` | 🟡 | Bug 修复 |
| `review` | 🔵 | Code Review |
| `tech` | 🟢 | 技术建设 |
| `doc` | 📝 | 文档输出 |
| `meeting` | 📅 | 会议 / 沟通 |
| `research` | 🔍 | 技术调研 |
| `other` | 🔧 | 其他 |

---

## 📖 命令速查

> 以下命令供**懂技术的人**或 **OpenClaw 自动调用**使用。
> **小白不需要记这些，说人话就行。**

### 记录任务

```bash
bash task-tracker.sh -t requirement -n "用户详情页" --files 3 --lines 800
bash task-tracker.sh -t bugfix -n "修复购物车 Bug" --bugs 1
bash task-tracker.sh -t review -n "Review PR#456" --reviews 1
bash task-tracker.sh -t doc -n "写文档" --notify  # 记录并推送提醒
```

### 生成报告

```bash
python3 report-generator.py              # 今日完整日报
python3 report-generator.py --brief      # 今日精简版
python3 report-generator.py --week       # 本周周报
python3 report-generator.py --month      # 本月月报
python3 report-generator.py --brief --send  # 生成并推送到聊天窗口
```

### 消息推送

```bash
bash notifier.sh -m "消息内容"                      # 默认方式推送
bash notifier.sh -m "消息内容" --channel telegram    # 指定渠道
bash notifier.sh -m "消息内容" --method none         # 仅 stdout
bash notifier.sh -m "消息内容" --dry-run             # 测试模式
```

### 管理配置

```bash
python3 config-manager.py show                        # 查看配置
python3 config-manager.py set trigger.mode auto_count # 修改触发方式
python3 config-manager.py set report_style.mode full  # 修改推送格式
python3 config-manager.py reset                       # 重置默认
```

---

## ⚙️ 配置速览

| 配置项 | 可选值 | 默认值 | 说明 |
|--------|--------|--------|------|
| `trigger.mode` | `manual` / `auto_count` / `auto_time` | `manual` | 什么时候触发日报 |
| `report_style.mode` | `brief` / `full` / `both` | `brief` | 日报详细程度 |
| `task_types.mode` | `preset_8` / `preset_4` / `custom` | `preset_8` | 任务类型数量 |
| `reminder.mode` | `count` / `always` / `never` | `count` | 提醒频率 |
| `reminder.count_threshold` | 数字 | `3` | 每 N 个任务提醒一次 |
| `notification.method` | `cli` / `webhook` / `none` | `cli` | 推送方式 |
| `notification.channel` | 渠道名 | 空 | 推送到哪（telegram 等） |

全部配置通过 `config.json` 管理，用 `config-manager.py` 修改，或直接跟 OpenClaw 说。

---

## 📚 开发手册

> 以下内容给**想二次开发**或**想了解内部实现**的人看。**小白可以跳过。**

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

---

## 🤔 常见问题

### 我不会 git，能用吗？

**能。** 你只需要会跟 OpenClaw 说人话。git、Python、Shell 这些东西，OpenClaw 全包了。

### 日报发到哪？

默认发到你当前的聊天窗口。想发到 Telegram / Discord / WhatsApp？跟 OpenClaw 说就行。

### 数据会丢吗？

**不会。** 任务记录实时写入文件（`data/YYYY-MM-DD.jsonl`），不是存在内存里。就算 OpenClaw 重启，数据还在。

### 免打扰怎么设置？

跟 OpenClaw 说：「晚上 11 点到早上 8 点不要推送」。它会自动修改配置。

### 我能自定义任务类型吗？

能。跟 OpenClaw 说：「加一个自定义任务类型：摸鱼」。它会帮你改配置。

---

## 📈 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=leisvip/daily-report&type=Timeline)](https://star-history.com/#leisvip/daily-report&Timeline)

---

## 📄 License

[MIT](LICENSE)

---

<div align="center">

**如果觉得有用，请给个 ⭐ Star 支持一下！**

**你的一颗 Star，就是赛博牛马的一天动力。** 🐂🐴

</div>
