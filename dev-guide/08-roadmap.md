---
title: 后续路线图
description: 功能规划、优先级分层、里程碑时间表。
date: 2026-04-29
---

# 08 · 后续路线图

## P0 — 核心增强（1-2 周）

- [x] **消息推送集成**：notifier.sh 封装，CLI 推送为主，Webhook 降级，stdout 保底
- [x] **task-tracker.sh 推送**：--notify 参数，达到阈值自动提醒
- [x] **report-generator.py 推送**：--send 参数，生成后直接推送到聊天窗口
- [x] **config.json notification 节点**：method/channel/target/webhook/quiet_hours
- [x] **config-manager.py notification 管理**：show/set 支持所有 notification 配置
- [ ] 自动从 Git 日志提取 commit 数和代码行数
- [ ] 任务去重（同名任务不重复记录）
- [ ] 支持 `--json` 参数输出原始 JSON
- [ ] 修复空 JSONL 文件导致的异常

## P1 — 功能扩展（2-4 周）

- [ ] 支持 Web 界面查看历史报告
- [ ] 支持导出为 CSV / Excel
- [ ] 支持多项目隔离（按项目名分目录）
- [ ] 添加任务耗时自动计时（开始 / 结束标记）
- [ ] 支持从 Jira / 飞书项目自动同步任务

## P2 — 智能化（1-2 月）

- [ ] AI 自动生成一句话总结（替代模板中的手动填写）
- [ ] 智能分类（根据任务描述自动判断类型）
- [ ] 趋势分析（本周 vs 上周对比、异常检测）
- [ ] 月度回顾报告（自动提炼亮点和成长点）

## P3 — 生态集成（长期）

- [ ] Hermes Agent 插件化（作为 Hermes Plugin 安装）
- [ ] OpenClaw Skill 化（作为 Skill 集成到技能库）
- [ ] GitHub Action 集成（CI/CD 中自动记录部署任务）
- [ ] 飞书 / Notion 同步（报告自动推送到文档平台）
- [ ] Telegram Bot 推送（定时自动发送日报）
