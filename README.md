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

`一句话记录任务` → `一句话查看日报` → `一句话推送到聊天窗口`

[![Version](https://img.shields.io/badge/version-v1.1.0-blue?style=flat-square)](https://github.com/leisvip/daily-report/releases)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/leisvip/daily-report?style=social)](https://github.com/leisvip/daily-report/stargazers)

[快速开始](#-快速开始) · [功能特性](#-功能特性) · [小白指南](#-小白指南动嘴就行) · [命令速查](#-命令速查) · [开发手册](#-开发手册)

</div>

---

## 🚀 快速开始

### 方式一：OpenClaw 对话安装（推荐，零命令行）

打开你和 OpenClaw 的对话窗口（Telegram / Discord / Web 都行），发送：

```
帮我安装赛博牛马日报项目：https://github.com/leisvip/daily-report
```

OpenClaw 会自动：

1. 克隆仓库到本地
2. 检查环境依赖（Python 3、bash）
3. 赋予脚本执行权限
4. 告诉你「装好了，可以用了」

**安装完就能直接用，不需要任何额外配置。**

### 方式二：手动安装（给想自己动手的人）

```bash
# 1. 克隆仓库
git clone https://github.com/leisvip/daily-report.git
cd daily-report

# 2. 赋予脚本执行权限
chmod +x task-tracker.sh notifier.sh

# 3. 验证安装
bash task-tracker.sh --help
python3 report-generator.py --help
```

**前置条件：** Python 3.6+、bash、git（仅方式二需要）

### 方式三：下载 zip（最简单）

1. 打开 https://github.com/leisvip/daily-report
2. 点绿色「Code」按钮 → 「Download ZIP」
3. 解压到任意目录
4. 赋予脚本执行权限：`chmod +x *.sh`

---

## ✨ 功能特性

### 🎯 自动打卡

每完成一个任务，自动记录到当日日志。支持 8 种任务类型：

| 类型 | Emoji | 说明 | 示例 |
|------|-------|------|------|
| `requirement` | 🔴 | 需求开发 | 写用户详情页、开发 API 接口 |
| `bugfix` | 🟡 | Bug 修复 | 修复购物车计算错误 |
| `review` | 🔵 | Code Review | Review PR#456 |
| `tech` | 🟢 | 技术建设 | 重构缓存模块、优化 CI |
| `doc` | 📝 | 文档输出 | 写 API 文档、更新 README |
| `meeting` | 📅 | 会议 / 沟通 | 需求评审、技术对齐 |
| `research` | 🔍 | 技术调研 | 调研消息队列选型 |
| `other` | 🔧 | 其他 | 部署、配置、杂活 |

### 📊 多维报表

| 报表类型 | 命令 | 说明 |
|----------|------|------|
| 今日精简版 | `日报` | 5-10 行，直接发到聊天窗口 |
| 今日完整版 | `完整日报` | 包含每个任务详情和量化数据 |
| 本周周报 | `周报` | 汇总本周所有任务 |
| 本月月报 | `月报` | 汇总本月所有任务 |

### 📡 三级降级推送

推送链路：`脚本 → notifier.sh → openclaw message send → 聊天窗口`

```
第 1 优先：openclaw message send（本地 CLI，最常用）
    ↓ 失败
第 2 优先：Webhook API（远程 / 服务器场景）
    ↓ 失败
第 3 优先：stdout 打印（保底，永远不丢数据）
```

支持推送到：Telegram、Discord、WhatsApp、Slack、Signal、iMessage 等。

### 🔔 智能提醒

完成 N 个任务后自动提醒「可以查看日报了」。阈值可配置。

### 🌙 免打扰

23:00 - 08:00 静默推送，不打扰休息。时段可自定义。

### ⚙️ 全可配置

所有选项通过 `config.json` 管理，支持运行时热修改，不需要重启。

---

## 🐣 小白指南：动嘴就行

### 场景一：记录任务

```
你：帮我记录一个任务：写周报，类型是需求开发，代码 500 行
AI：✅ 任务已记录 [requirement] 写周报
    📊 今日已完成: 1 个任务
```

OpenClaw 背后做了什么：

```bash
bash task-tracker.sh -t requirement -n "写周报" --lines 500
```

**你不需要知道这行命令，你只需要说人话。**

### 场景二：查看日报

```
你：日报
AI：═══════════════════════════════════════
      📋 今日日报 - 2026.04.29（周二）
    ═══════════════════════════════════════
    ✅ 完成任务 3 个
    🔴 需求开发: 写周报
    🟡 Bug 修复: 修复购物车
    🔵 Code Review: Review PR#456
    📊 500行 · 3个文件
```

OpenClaw 背后做了什么：

```bash
python3 report-generator.py --brief
```

### 场景三：推送到指定渠道

```
你：把日报发到 Telegram
AI：✅ 日报已推送到 Telegram
```

OpenClaw 背后做了什么：

```bash
python3 report-generator.py --brief --send --channel telegram
```

推送链路：`report-generator.py → notifier.sh → openclaw message send → Telegram`

### 场景四：查看周报 / 月报

```
你：周报
你：月报
```

### 场景五：改配置

```
你：把提醒改成每个任务都提醒
你：日报用完整版格式
你：免打扰改成晚上 10 点到早上 7 点
```

---

## 🎯 你可以说的话（OpenClaw 指令映射）

| 你说 | OpenClaw 做 |
|------|-------------|
| "记录任务：写文档" | `task-tracker.sh -t other -n "写文档"` |
| "记录需求：用户详情页，800 行" | `task-tracker.sh -t requirement -n "用户详情页" --lines 800` |
| "记录 Bug：修复购物车" | `task-tracker.sh -t bugfix -n "修复购物车"` |
| "记录 Review：PR#456" | `task-tracker.sh -t review -n "Review PR#456"` |
| "日报" | `report-generator.py --brief` |
| "完整日报" | `report-generator.py` |
| "周报" | `report-generator.py --week` |
| "月报" | `report-generator.py --month` |
| "发到 Telegram" | `report-generator.py --brief --send --channel telegram` |
| "发到 Discord" | `report-generator.py --brief --send --channel discord` |
| "查看配置" | `config-manager.py show` |
| "改提醒模式" | `config-manager.py set reminder.mode <值>` |
| "今天干了几件事？" | 读取日志，统计行数 |
| "重置配置" | `config-manager.py reset` |

---

## 📖 命令速查

> 以下命令供**懂技术的人**或 **OpenClaw 自动调用**使用。
> **小白不需要记这些，说人话就行。**

### 记录任务

```bash
# 基础用法
bash task-tracker.sh -t requirement -n "用户详情页" --lines 800 --files 3

# 记录 Bug
bash task-tracker.sh -t bugfix -n "修复购物车 Bug" --bugs 1

# 记录 Review
bash task-tracker.sh -t review -n "Review PR#456" --reviews 1

# 记录并推送提醒到聊天窗口
bash task-tracker.sh -t doc -n "写文档" --notify

# 指定推送渠道
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
bash notifier.sh -m "消息内容"                           # 默认推送
bash notifier.sh -m "消息内容" --channel telegram          # 指定渠道
bash notifier.sh -m "消息内容" --method none               # 仅 stdout
bash notifier.sh -m "消息内容" --dry-run                   # 测试模式
```

### 管理配置

```bash
python3 config-manager.py show                        # 查看配置
python3 config-manager.py set trigger.mode auto_count # 修改触发方式
python3 config-manager.py set report_style.mode full  # 修改推送格式
python3 config-manager.py set reminder.mode never     # 关闭提醒
python3 config-manager.py reset                       # 重置默认
```

---

## ⚙️ 配置速览

所有选项通过 `config.json` + `config-manager.py` 管理，或直接跟 OpenClaw 说。

| 配置项 | 可选值 | 默认值 | 说明 |
|--------|--------|--------|------|
| `trigger.mode` | `manual` / `auto_count` / `auto_time` | `manual` | 什么时候触发日报 |
| `report_style.mode` | `brief` / `full` / `both` | `brief` | 日报详细程度 |
| `task_types.mode` | `preset_8` / `preset_4` / `custom` | `preset_8` | 任务类型数量 |
| `reminder.mode` | `count` / `always` / `never` | `count` | 提醒频率 |
| `reminder.count_threshold` | 数字 | `3` | 每 N 个任务提醒一次 |
| `notification.method` | `cli` / `webhook` / `none` | `cli` | 推送方式 |
| `notification.channel` | 渠道名 | 空 | 推送到哪（telegram 等） |
| `notification.quiet_hours` | 时间段 | `23:00 - 08:00` | 免打扰时段 |

---

## 📁 项目结构

```
daily-report/
├── task-tracker.sh          # 任务记录器（每完成任务调用一次）
├── report-generator.py      # 日报 / 周报 / 月报生成器
├── notifier.sh              # 消息推送封装（CLI → Webhook → stdout）
├── config-manager.py        # 配置管理器（查看 / 修改 / 重置）
├── config.json              # 配置中心
├── data/                    # 每日任务日志（运行时自动创建）
│   └── YYYY-MM-DD.jsonl     #   一行一条 JSON，追加写入
├── reports/                 # 生成的报告文件（运行时自动创建）
│   └── YYYY-MM-DD.md
├── dev-guide/               # 开发手册（8 章）
│   ├── 01-architecture.md   #   架构详解
│   ├── 02-dev-setup.md      #   环境搭建
│   ├── 03-module-guide.md   #   模块开发
│   ├── 04-api-reference.md  #   API 参考
│   ├── 05-testing.md        #   测试指南
│   ├── 06-deployment.md     #   部署打包
│   ├── 07-troubleshooting.md#   排错手册
│   └── 08-roadmap.md        #   路线图
└── docs/                    # 设计文档
    ├── 方案设计书.md
    └── 集成方案-OpenClaw消息推送.md
```

---

## 🧠 架构一览

> 以下内容给想了解原理的人看。**小白可以跳过。**

### 数据流

```
你说话 → OpenClaw 理解意图 → 调用脚本 → 写入日志 → 生成报告 → 推送到聊天窗口
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

### 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 任务记录器 | Bash | 零依赖，追加写入 JSONL |
| 报告生成器 | Python 3 | JSON 处理、模板渲染 |
| 消息推送 | Bash + OpenClaw CLI | 三级降级，永远不丢 |
| 配置管理 | Python 3 + JSON | 运行时热修改 |
| 数据存储 | JSONL 文件 | 按日分文件，永久可查 |

---

## 🤔 常见问题

### 我不会 git，能用吗？

**能。** 你只需要会跟 OpenClaw 说人话。git、Python、Shell 这些东西，OpenClaw 全包了。

### 日报发到哪？

默认发到你当前的聊天窗口。想发到 Telegram / Discord / WhatsApp？跟 OpenClaw 说「把日报发到 Telegram」就行。

### 数据会丢吗？

**不会。** 任务记录实时写入文件（`data/YYYY-MM-DD.jsonl`），不是存在内存里。就算 OpenClaw 重启，数据还在。

### 推送失败怎么办？

系统会自动降级：CLI 推送失败 → 尝试 Webhook → 最终打印到 stdout。永远不丢数据。

### 能自定义任务类型吗？

能。跟 OpenClaw 说「加一个自定义任务类型：摸鱼」，或直接编辑 `config.json`。

### 免打扰怎么设置？

跟 OpenClaw 说「晚上 11 点到早上 8 点不要推送」。它会自动修改配置。

### 周报 / 月报怎么出？

积累够数据后，跟 OpenClaw 说「周报」或「月报」就行。系统会自动汇总对应时间段的所有任务。

---

## 📚 开发手册

完整开发文档见 [`dev-guide/`](dev-guide/)：

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
