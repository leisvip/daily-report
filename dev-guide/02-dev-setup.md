---
title: 环境搭建与快速开始
description: 环境要求、安装步骤、目录结构、命令速查。
date: 2026-04-29
---

# 02 · 环境搭建与快速开始

## 环境要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | >= 3.6 | 报告生成器、配置管理器 |
| Bash | >= 4.0 | 任务记录器 |

无需额外安装任何第三方库，全部使用标准库。

## 目录结构

```
daily-report/
├── config.json              # 配置中心（所有选项随时可调）
├── config-manager.py        # 配置管理器
├── task-tracker.sh          # 任务记录器
├── report-generator.py      # 日报 / 周报 / 月报生成器
├── notifier.sh              # 消息推送封装（CLI / Webhook / stdout）
├── README.md                # 使用说明
├── dev-guide/               # 开发手册（本目录）
├── data/                    # 运行时数据（自动创建）
│   └── YYYY-MM-DD.jsonl     # 每日任务日志
└── reports/                 # 生成的报告（自动创建）
    └── YYYY-MM-DD.md        # 日报文件
```

## 快速搭建

```bash
cd daily-report
chmod +x task-tracker.sh notifier.sh
```

验证安装：

```bash
bash task-tracker.sh -h
python3 report-generator.py --help
python3 config-manager.py show
```

## 命令速查

### 记录任务

| 命令 | 说明 |
|------|------|
| `bash task-tracker.sh -t requirement -n "名称"` | 记录需求开发 |
| `bash task-tracker.sh -t bugfix -n "名称" --bugs 1` | 记录 Bug 修复 |
| `bash task-tracker.sh -t review -n "名称" --reviews 1` | 记录 Code Review |
| `bash task-tracker.sh -t doc -n "名称" --lines 2000` | 记录文档输出 |
| `bash task-tracker.sh -t tech -n "名称" --files 5` | 记录技术建设 |
| `bash task-tracker.sh -t requirement -n "名称" --notify` | 记录并推送提醒 |

### 生成报告

| 命令 | 说明 |
|------|------|
| `python3 report-generator.py` | 今日完整日报 |
| `python3 report-generator.py --brief` | 今日精简版 |
| `python3 report-generator.py --week` | 本周周报 |
| `python3 report-generator.py --month` | 本月月报 |
| `python3 report-generator.py --date 2026-04-28` | 指定日期 |
| `python3 report-generator.py --brief --send` | 精简版并推送 |

### 消息推送

| 命令 | 说明 |
|------|------|
| `bash notifier.sh -m "消息"` | 默认方式推送 |
| `bash notifier.sh -m "消息" --channel telegram` | 指定渠道推送 |
| `bash notifier.sh -m "消息" --method none` | 仅 stdout |
| `bash notifier.sh -m "消息" --dry-run` | 测试模式 |

### 管理配置

| 命令 | 说明 |
|------|------|
| `python3 config-manager.py show` | 查看当前配置 |
| `python3 config-manager.py set key value` | 修改配置项 |
| `python3 config-manager.py reset` | 重置为默认 |

## 调试技巧

查看当日日志内容：

```bash
cat data/$(date +%Y-%m-%d).jsonl | python3 -m json.tool --no-ensure-ascii
```

手动触发日报生成并查看输出：

```bash
python3 report-generator.py --brief 2>&1
```

检查配置是否生效：

```bash
python3 -c "import json; print(json.dumps(json.load(open('config.json')), indent=2, ensure_ascii=False))"
```
