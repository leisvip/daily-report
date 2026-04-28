---
title: 测试指南
description: 验证任务记录、报告生成、配置管理的完整流程。
date: 2026-04-29
---

# 05 · 测试指南

## 手动验证流程

### 测试任务记录

```bash
# 基础记录
bash task-tracker.sh -t requirement -n "测试任务" -d "描述" --lines 100 --files 2

# 验证 JSONL 写入
tail -1 data/$(date +%Y-%m-%d).jsonl | python3 -m json.tool

# 验证计数
wc -l data/$(date +%Y-%m-%d).jsonl
```

### 测试报告生成

```bash
# 先写入 3 条测试数据
bash task-tracker.sh -t requirement -n "任务A" --lines 500
bash task-tracker.sh -t bugfix -n "修复B" --bugs 1
bash task-tracker.sh -t doc -n "写文档" --lines 1000

# 生成精简版
python3 report-generator.py --brief

# 生成完整版
python3 report-generator.py

# 验证文件已保存
ls -la reports/
```

### 测试配置管理

```bash
# 查看
python3 config-manager.py show

# 修改
python3 config-manager.py set trigger.mode auto_count
python3 config-manager.py set reminder.count_threshold 5

# 验证修改
python3 config-manager.py show | grep -A1 "触发方式"

# 重置
python3 config-manager.py reset
```

### 测试消息推送

```bash
# notifier.sh 基础测试（method=none 仅 stdout）
bash notifier.sh -m "测试消息" --method none

# notifier.sh dry-run（不实际推送）
bash notifier.sh -m "测试消息" --method cli --dry-run

# task-tracker.sh --notify 测试
bash task-tracker.sh -t tech -n "推送测试" --notify

# report-generator.py --send 测试
python3 report-generator.py --brief --send

# 降级测试（webhook 无 token 时降级到 stdout）
bash notifier.sh -m "降级测试" --method webhook
```

### 测试配置管理（notification）

```bash
# 查看 notification 配置
python3 config-manager.py show | grep -A8 "Q6"

# 修改推送方式
python3 config-manager.py set notification.method none

# 修改推送渠道
python3 config-manager.py set notification.channel telegram

# 重置
python3 config-manager.py reset
```

## 验证清单

| 测试项 | 命令 | 预期结果 |
|--------|------|----------|
| 记录任务 | `bash task-tracker.sh -t other -n "test"` | 输出「任务已记录」 |
| JSONL 格式 | `tail -1 data/*.jsonl \| python3 -m json.tool` | 合法 JSON |
| 精简版报告 | `python3 report-generator.py --brief` | 输出 5-15 行 |
| 完整版报告 | `python3 report-generator.py` | 输出含表格和热力图 |
| 配置修改 | `python3 config-manager.py set X Y` | 输出「✅ X → Y」 |
| 空日期处理 | `python3 report-generator.py --date 2099-01-01` | 输出「暂无记录」 |
| 周报生成 | `python3 report-generator.py --week` | 输出周报 |
| 月报生成 | `python3 report-generator.py --month` | 输出月报 |
| notifier 基础 | `bash notifier.sh -m "test" --method none` | 输出消息 |
| notifier dry-run | `bash notifier.sh -m "test" --dry-run` | 输出消息 |
| task-tracker --notify | `bash task-tracker.sh -t other -n "test" --notify` | 输出「任务已记录」+ 推送 |
| report --send | `python3 report-generator.py --brief --send` | 输出精简版 + 推送 |
| notification 配置 | `python3 config-manager.py show` | 显示 Q6 消息推送 |
| 降级 stdout | `bash notifier.sh -m "test" --method webhook` | 降级到 stdout |
