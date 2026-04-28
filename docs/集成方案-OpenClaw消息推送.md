---
title: daily-report 真正集成 OpenClaw 消息接口 — 执行方案
description: 将日报系统的"打印到 stdout"改为脚本主动调用 OpenClaw 消息接口，实现自动推送到聊天窗口。
tags: [daily-report, OpenClaw, 集成, 消息推送]
date: 2026-04-29
---

# daily-report 真正集成 OpenClaw 消息接口 — 执行方案

> **目标**：让 `task-tracker.sh` 和 `report-generator.py` 能主动调用 OpenClaw 的消息接口，将日报/提醒直接推送到用户的聊天窗口（Telegram / Discord / WhatsApp 等），不再依赖 AI 手动转发 stdout。

---

## 一、问题分析

### 1.1 现状（伪集成）

```
用户说"日报"
    → AI 调用 report-generator.py --brief
    → Python 打印到 stdout
    → AI 读取 stdout 内容
    → AI 用 message 工具发给用户
```

**问题**：

- 推送完全依赖 AI 中转，脚本自身无法主动推送
- AI 重启/遗忘时日报推不出去
- `task-tracker.sh` 的提醒（"已完成 3 个任务"）也只是打印，用户看不到
- 无法实现定时自动推送（如每天 23:00 自动生成并推送）

### 1.2 目标（真集成）

```
report-generator.py --brief --send
    → 脚本内部调用 OpenClaw 消息接口
    → 消息直接到达用户聊天窗口

task-tracker.sh -t requirement -n "写文档" --notify
    → 记录任务
    → 达到阈值时主动推送提醒到聊天窗口
```

---

## 二、集成方案对比

### 2.1 三种可行路径

| 方案 | 实现方式 | 优点 | 缺点 | 推荐 |
|------|----------|------|------|------|
| **A. CLI 调用** | 脚本内执行 `openclaw message send` | 最简单，零依赖，直接可用 | 需要 openclaw CLI 在 PATH 中 | ⭐⭐⭐⭐⭐ |
| **B. Webhook API** | 脚本内 curl POST 到 `/hooks/wake` | 远程可用，不依赖本地 CLI | 需要 hooks 配置开启、token 管理 | ⭐⭐⭐⭐ |
| **C. Cron 定时** | 用 OpenClaw cron 创建定时任务 | 完全自动，无需脚本触发 | 灵活度低，无法"任务完成时"触发 | ⭐⭐⭐ |

### 2.2 推荐决策：方案 A + B 组合

- **日常推送**：方案 A（`openclaw message send`），脚本直接调用 CLI
- **远程/定时场景**：方案 B（Webhook API），通过 HTTP 接口触发
- **Cron 辅助**：可选配置每日定时生成日报的 cron job

---

## 三、详细设计

### 3.1 新增模块：`notifier.sh`（消息推送封装）

统一的消息推送入口，屏蔽 CLI / API 差异，供 `task-tracker.sh` 和 `report-generator.py` 调用。

```bash
#!/usr/bin/env bash
# notifier.sh — OpenClaw 消息推送封装
# 调用方式: bash notifier.sh --message "内容" [--channel telegram] [--target @user]

# 优先使用 openclaw message send
# 降级使用 webhook API
# 最终降级到 stdout（保证不丢失）
```

**推送优先级**：

```
1. openclaw message send（本地 CLI 可用时）
        ↓ 失败
2. webhook API（配置了 hooks 时）
        ↓ 失败
3. stdout 打印（保底，永远不丢数据）
```

### 3.2 `task-tracker.sh` 改造

**新增参数**：

| 参数 | 说明 | 示例 |
|------|------|------|
| `--notify` | 完成后推送提醒到聊天窗口 | `--notify` |
| `--channel` | 指定推送渠道 | `--channel telegram` |
| `--target` | 指定推送目标 | `--target @user` |

**改造逻辑**：

```bash
# 原来：只打印到 stdout
echo "✅ 任务已记录 [$TYPE] $NAME"
echo "   📊 今日已完成: ${TOTAL} 个任务"

# 改造后：
# 1. 仍然打印到 stdout（保底）
# 2. 如果 --notify，调用 notifier.sh 推送
# 3. 达到提醒阈值时，自动推送提醒消息
```

**触发条件**（与 config.json 的 reminder 配置联动）：

| 条件 | 推送内容 |
|------|----------|
| `--notify` 显式指定 | 推送"✅ 任务已记录" |
| 任务数达到 `count_threshold` | 推送"💡 今日已完成 N 个任务，可以说「日报」查看" |
| 不满足条件 | 静默（仅 stdout） |

### 3.3 `report-generator.py` 改造

**新增参数**：

| 参数 | 说明 | 示例 |
|------|------|------|
| `--send` | 生成后直接推送到聊天窗口 | `--brief --send` |
| `--channel` | 指定推送渠道 | `--channel telegram` |
| `--target` | 指定推送目标 | `--target @user` |

**改造逻辑**：

```python
# 原来：只打印到 stdout
print(generate_brief(date_str, tasks))

# 改造后：
# 1. 生成报告内容
# 2. 如果 --send，调用 notifier.sh 推送
# 3. 仍然保存到文件（如果 --save）
# 4. 仍然打印到 stdout
```

### 3.4 配置文件扩展

`config.json` 新增 `notification` 节点：

```json
{
  "notification": {
    "_doc": "消息推送配置",
    "_options": "cli | webhook | none",
    "method": "cli",
    "channel": "",
    "target": "",
    "webhook": {
      "url": "http://127.0.0.1:18789/hooks/wake",
      "token": "",
      "timeout": 10
    },
    "quiet_hours": {
      "enabled": true,
      "start": "23:00",
      "end": "08:00"
    }
  }
}
```

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `method` | 推送方式：`cli`（本地 CLI）/ `webhook`（HTTP API）/ `none`（关闭） | `cli` |
| `channel` | 聊天渠道（telegram / discord / whatsapp 等） | 空（自动检测） |
| `target` | 推送目标（用户 ID / chat ID） | 空（发给当前会话） |
| `webhook.url` | Webhook 端点地址 | `http://127.0.0.1:18789/hooks/wake` |
| `webhook.token` | Webhook 认证 token | 空 |
| `quiet_hours` | 免打扰时段（不推送） | 23:00 - 08:00 |

---

## 四、执行流程图

### 4.1 任务记录 + 推送流程

```
task-tracker.sh -t requirement -n "写文档" --notify
    │
    ├── 1. 参数解析
    ├── 2. 构建 JSON 条目
    ├── 3. 追加写入 data/YYYY-MM-DD.jsonl
    ├── 4. 打印到 stdout（保底）
    │
    ├── 5. 检查 --notify 标志
    │       │
    │       ├── 是 → 调用 notifier.sh 推送"✅ 任务已记录"
    │       └── 否 → 跳过
    │
    └── 6. 检查任务数是否达到阈值
            │
            ├── 达到 → 调用 notifier.sh 推送"💡 可以查看日报了"
            └── 未达到 → 静默
```

### 4.2 日报生成 + 推送流程

```
report-generator.py --brief --send
    │
    ├── 1. 读取 data/YYYY-MM-DD.jsonl
    ├── 2. 按类型分类汇总
    ├── 3. 生成精简版 / 完整版
    ├── 4. 打印到 stdout
    ├── 5. 保存到 reports/YYYY-MM-DD.md（如果 --save）
    │
    └── 6. 检查 --send 标志
            │
            ├── 是 → 调用 notifier.sh 推送报告内容
            │         │
            │         ├── 检查 quiet_hours → 免打扰则跳过
            │         ├── method=cli → openclaw message send
            │         ├── method=webhook → curl POST
            │         └── method=none → 跳过
            │
            └── 否 → 结束
```

### 4.3 notifier.sh 推送决策流

```
notifier.sh --message "内容" [--channel X] [--target Y]
    │
    ├── 1. 读取 config.json notification 配置
    ├── 2. 合并参数（命令行 > 配置文件 > 默认值）
    ├── 3. 检查 quiet_hours → 在免打扰时段则跳过
    │
    ├── 4. 尝试推送
    │       │
    │       ├── method=cli
    │       │     └── openclaw message send --message "内容" [--channel X] [--target Y]
    │       │           │
    │       │           ├── 成功 → 结束
    │       │           └── 失败 → 降级到 method=webhook
    │       │
    │       ├── method=webhook
    │       │     └── curl -X POST http://127.0.0.1:18789/hooks/wake
    │       │           -H "Authorization: Bearer $TOKEN"
    │       │           -d '{"text":"内容","mode":"now"}'
    │       │           │
    │       │           ├── 成功 → 结束
    │       │           └── 失败 → 降级到 stdout
    │       │
    │       └── method=none → 跳过
    │
    └── 5. 降级：打印到 stdout（保证信息不丢失）
```

---

## 五、需要修改的文件清单

| 文件 | 操作 | 改动说明 |
|------|------|----------|
| `notifier.sh` | **新增** | 消息推送封装脚本（~80 行） |
| `task-tracker.sh` | **修改** | 新增 `--notify` / `--channel` / `--target` 参数，末尾调用 notifier.sh |
| `report-generator.py` | **修改** | 新增 `--send` / `--channel` / `--target` 参数，末尾调用 notifier.sh |
| `config.json` | **修改** | 新增 `notification` 配置节点 |
| `config-manager.py` | **修改** | 支持管理 `notification.*` 配置项 |
| `dev-guide/01-architecture.md` | **修改** | 更新架构图，加入 notifier 模块 |
| `dev-guide/04-api-reference.md` | **修改** | 更新 CLI 参数文档 |
| `dev-guide/08-roadmap.md` | **修改** | 标记已完成项，更新路线图 |
| `README.md` | **修改** | 更新命令速查和配置速览 |

---

## 六、前置条件检查

### 6.1 OpenClaw CLI 可用性

```bash
# 检查 openclaw 是否在 PATH 中
which openclaw

# 检查 message send 是否可用
openclaw message send --help
```

### 6.2 消息渠道配置

```bash
# 检查当前配置了哪些渠道
openclaw channels list

# 或查看配置
openclaw config get channels
```

### 6.3 Webhook 配置（如果用方案 B）

```bash
# 检查 hooks 是否启用
openclaw config get hooks
```

---

## 七、风险评估

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| `openclaw` CLI 不在 PATH 中 | 低 | 推送失败 | 降级到 stdout，不丢数据 |
| 消息渠道未配置 | 中 | 推送失败 | notifier.sh 检测并提示 |
| quiet_hours 误拦截 | 低 | 消息延迟 | 可配置关闭 |
| Webhook token 泄露 | 低 | 安全风险 | token 存本地 config.json，不外发 |
| `openclaw message send` 超时 | 低 | 推送延迟 | 设置 10s 超时，降级到 stdout |

---

## 八、执行步骤

| 步骤 | 内容 | 预计耗时 |
|------|------|----------|
| Step 1 | 检查前置条件（CLI 可用性、渠道配置） | 2 分钟 |
| Step 2 | 创建 `notifier.sh` 推送封装脚本 | 10 分钟 |
| Step 3 | 改造 `task-tracker.sh`（新增推送参数 + 调用 notifier） | 8 分钟 |
| Step 4 | 改造 `report-generator.py`（新增 --send 参数 + 调用 notifier） | 10 分钟 |
| Step 5 | 扩展 `config.json`（新增 notification 节点） | 3 分钟 |
| Step 6 | 扩展 `config-manager.py`（支持 notification 配置管理） | 5 分钟 |
| Step 7 | 更新 dev-guide 文档（架构图、API 参考、路线图） | 10 分钟 |
| Step 8 | 端到端测试（记录任务 → 推送提醒 → 生成日报 → 推送日报） | 5 分钟 |
| Step 9 | 更新 README.md | 3 分钟 |
| **总计** | | **~56 分钟** |

---

## 九、待决策项

### Q1: 推送方案选择

- **A. 方案 A（CLI 调用）为主 + 方案 B（Webhook）降级**（推荐 ✅）
  - 最简单直接，先跑起来再优化
- B. 只用方案 A（CLI）
  - 更简单，但远程场景不可用
- C. 只用方案 B（Webhook）
  - 需要额外配置 hooks，增加复杂度

### Q2: 默认推送行为

- **A. 默认不推送，需要显式 `--send` / `--notify`**（推荐 ✅）
  - 不打扰用户，按需推送
- B. 默认推送，用 `--no-send` 关闭
  - 更积极，但可能打扰
- C. 根据 config.json 的 `trigger.mode` 决定
  - 灵活但复杂

### Q3: 是否保留 stdout 输出

- **A. 推送时仍然打印到 stdout（双写）**（推荐 ✅）
  - 保底不丢数据，日志可查
- B. 推送成功后不再打印到 stdout
  - 更干净，但丢数据风险

### Q4: 免打扰时段

- **A. 继承现有 reminder.quiet_hours 配置**（推荐 ✅）
  - 统一管理，不重复配置
- B. notification 单独配置 quiet_hours
  - 独立控制，但配置冗余

---

## 十、验证标准

改造完成后，以下场景必须通过：

```
场景 1: 手动推送日报
  $ python3 report-generator.py --brief --send
  → stdout 打印精简版
  → 聊天窗口收到精简版消息 ✅

场景 2: 记录任务 + 推送提醒
  $ bash task-tracker.sh -t requirement -n "测试推送" --notify
  → stdout 打印"✅ 任务已记录"
  → 聊天窗口收到提醒消息 ✅

场景 3: 达到阈值自动提醒
  $ bash task-tracker.sh -t other -n "第3个任务"
  → stdout 打印记录 + "💡 可以查看日报了"
  → 聊天窗口收到提醒消息 ✅

场景 4: 降级（CLI 不可用时）
  $ 模拟 openclaw 命令不存在
  → 仍然打印到 stdout，不报错 ✅

场景 5: 免打扰时段
  $ 在 23:30 推送日报
  → stdout 打印，但聊天窗口不推送 ✅
```

---

*方案版本：v1.0*
*设计时间：2026-04-29*
*等待决策：✅ 是 / ❌ 否 / 🔧 修改后执行*
