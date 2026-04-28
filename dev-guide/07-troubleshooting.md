---
title: 常见问题与排错
description: 启动、运行、配置、报告生成相关问题的排查与解决。
date: 2026-04-29
---

# 07 · 常见问题与排错

## 启动类

### Q: `bash task-tracker.sh` 报 `Permission denied`

- **原因**：脚本没有执行权限
- **解决**：`chmod +x task-tracker.sh`

### Q: `python3 report-generator.py` 报 `No module named 'xxx'`

- **原因**：使用了非标准 Python 版本
- **解决**：确认 `python3 --version` >= 3.6

## 数据类

### Q: 日报显示「暂无任务记录」

- **原因**：当日 JSONL 文件不存在或为空
- **解决**：先用 `task-tracker.sh` 记录至少一条任务

### Q: JSONL 文件内容损坏

- **原因**：手动编辑导致 JSON 格式错误
- **解决**：`python3 -c "import json; [json.loads(l) for l in open('data/YYYY-MM-DD.jsonl')]"` 定位错误行

### Q: 指标数据不累加

- **原因**：JSONL 中某条记录的 metrics 字段缺失
- **解决**：report-generator 使用 `.get("field", 0)` 兜底，缺失字段按 0 处理

## 配置类

### Q: `config-manager.py set` 修改后不生效

- **原因**：修改了错误的 config.json 路径
- **解决**：确认在 `daily-report/` 目录下执行

### Q: 任务类型自定义后报告中不显示 emoji

- **原因**：自定义类型缺少 emoji 字段
- **解决**：在 `config.json` 的类型定义中补充 `"emoji": "🔧"`

## 报告类

### Q: 精简版输出超过配置的行数上限

- **原因**：任务类型过多，每类一行会超限
- **解决**：减少 `task_types.mode` 中的类型数量（改用 `preset_4`）

### Q: 周报 / 月报数据为空

- **原因**：对应时间段没有 JSONL 文件
- **解决**：确认 `data/` 目录下有对应日期的文件

### Q: 报告中数字显示为 `0` 但仍输出

- **原因**：模板中缺少 `if` 判断
- **解决**：报告模板中已做判断，`0` 值行不会输出

## 推送类

### Q: `--notify` / `--send` 后聊天窗口没有收到消息

- **原因**：`notification.channel` 和 `notification.target` 未配置
- **解决**：`python3 config-manager.py set notification.channel telegram`，然后设置 target
- **降级**：消息仍会打印到 stdout，不会丢失

### Q: notifier.sh 报 `openclaw: command not found`

- **原因**：OpenClaw CLI 不在 PATH 中
- **解决**：`which openclaw` 确认安装，或用 `--method webhook` 切换到 Webhook 模式
- **降级**：自动降级到 stdout 输出

### Q: Webhook 推送返回 401

- **原因**：`notification.webhook.token` 未配置或不匹配
- **解决**：`python3 config-manager.py set notification.webhook.token <your-token>`

### Q: 免打扰时段内消息没有推送

- **原因**：`notification.quiet_hours.enabled` 为 true
- **解决**：修改免打扰时段或关闭：`python3 config-manager.py set notification.quiet_hours.enabled false`

### Q: notifier.sh 推送超时

- **原因**：OpenClaw Gateway 未启动或网络不通
- **解决**：`openclaw gateway status` 检查状态，或切换到 `--method none` 仅 stdout
