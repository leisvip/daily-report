#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
#  report-generator.py — 日报/周报/月报生成器
#  读取 JSONL 日志，套用模板，生成格式化报告
# ═══════════════════════════════════════════════════════════════

import json
import os
import sys
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "config.json"

# ── 加载配置 ──
def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

CFG = load_config()
DATA_DIR = SCRIPT_DIR / CFG["general"]["data_dir"]
REPORT_DIR = SCRIPT_DIR / CFG["general"]["report_dir"]
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ── 任务类型配置 ──
def get_task_types():
    mode = CFG["task_types"]["mode"]
    if mode == "preset_4":
        return CFG["task_types"]["preset_4_types"]
    return CFG["task_types"]["types"]

TASK_TYPES = get_task_types()

# ── 读取某日的任务日志 ──
def load_tasks(date_str):
    log_file = DATA_DIR / f"{date_str}.jsonl"
    tasks = []
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        tasks.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return tasks

# ── 读取某周的任务日志 ──
def load_week_tasks(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    week_start = dt - timedelta(days=dt.weekday())  # Monday
    tasks = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        tasks.extend(load_tasks(day.strftime("%Y-%m-%d")))
    return tasks, week_start.strftime("%Y-%m-%d"), (week_start + timedelta(days=6)).strftime("%Y-%m-%d")

# ── 读取某月的任务日志 ──
def load_month_tasks(year, month):
    tasks = []
    for day in range(1, 32):
        try:
            dt = datetime(year, month, day)
            tasks.extend(load_tasks(dt.strftime("%Y-%m-%d")))
        except ValueError:
            break
    return tasks

# ── 汇总统计 ──
def summarize(tasks):
    by_type = defaultdict(list)
    totals = {
        "total": len(tasks),
        "lines": 0, "files": 0, "commits": 0,
        "bugs": 0, "reviews": 0, "duration": 0
    }

    for t in tasks:
        ttype = t.get("type", "other")
        by_type[ttype].append(t)
        m = t.get("metrics", {})
        totals["lines"] += m.get("lines", 0)
        totals["files"] += m.get("files", 0)
        totals["commits"] += m.get("commits", 0)
        totals["bugs"] += m.get("bugs", 0)
        totals["reviews"] += m.get("reviews", 0)
        totals["duration"] += m.get("duration_min", 0)

    return dict(by_type), totals

# ── 格式化数字 ──
def fmt_num(n):
    if n >= 10000:
        return f"{n/10000:.1f}万"
    return f"{n:,}"

# ── 生成日报 Markdown ──
def generate_daily_report(date_str, tasks):
    by_type, totals = summarize(tasks)
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday = weekdays[dt.weekday()]

    lines = []
    lines.append(f"# 📋 今日日报 - {date_str}（{weekday}）")
    lines.append("")
    lines.append(f"> 📌 共完成 **{totals['total']}** 个任务")
    lines.append("")

    # 按类型输出
    type_order = ["requirement", "bugfix", "review", "tech", "doc", "meeting", "research", "other"]
    for ttype in type_order:
        if ttype not in by_type:
            continue
        type_tasks = by_type[ttype]
        info = TASK_TYPES.get(ttype, {"emoji": "🔧", "label": ttype})
        lines.append(f"### {info['emoji']} {info['label']}（{len(type_tasks)}）")
        for i, t in enumerate(type_tasks, 1):
            name = t.get("name", "未命名")
            desc = t.get("desc", "")
            status_icon = "✅" if t.get("status") == "done" else ("🚧" if t.get("status") == "wip" else "⚠️")
            lines.append(f"{i}. **{name}** {status_icon}")
            if desc:
                lines.append(f"   - {desc}")
            m = t.get("metrics", {})
            metric_parts = []
            if m.get("lines"): metric_parts.append(f"{fmt_num(m['lines'])} 行")
            if m.get("files"): metric_parts.append(f"{m['files']} 个文件")
            if m.get("commits"): metric_parts.append(f"{m['commits']} 个 commit")
            if m.get("bugs"): metric_parts.append(f"修复 {m['bugs']} 个 Bug")
            if m.get("reviews"): metric_parts.append(f"Review {m['reviews']} 次")
            if m.get("duration_min"): metric_parts.append(f"耗时 {m['duration_min']} 分钟")
            if metric_parts:
                lines.append(f"   - 📊 {' · '.join(metric_parts)}")
        lines.append("")

    # 量化数据表
    lines.append("## 📊 量化数据")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 总任务数 | {totals['total']} |")
    if totals["lines"]: lines.append(f"| 代码/文档行数 | {fmt_num(totals['lines'])} |")
    if totals["files"]: lines.append(f"| 涉及文件数 | {totals['files']} |")
    if totals["commits"]: lines.append(f"| Git Commit | {totals['commits']} |")
    if totals["bugs"]: lines.append(f"| Bug 修复 | {totals['bugs']} |")
    if totals["reviews"]: lines.append(f"| Code Review | {totals['reviews']} |")
    if totals["duration"]: lines.append(f"| 总耗时 | {totals['duration']} 分钟 |")
    lines.append("")

    # 进行中 / 阻塞
    wip = [t for t in tasks if t.get("status") == "wip"]
    blocked = [t for t in tasks if t.get("status") == "blocked"]
    if wip:
        lines.append("## 🚧 进行中")
        for t in wip:
            lines.append(f"- {t.get('name', '未命名')}")
        lines.append("")
    if blocked:
        lines.append("## ⚠️ 阻塞项")
        for t in blocked:
            lines.append(f"- {t.get('name', '未命名')}")
        lines.append("")

    lines.append("---")
    lines.append(f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    return "\n".join(lines)

# ── 生成精简版（聊天推送用） ──
def generate_brief(date_str, tasks):
    by_type, totals = summarize(tasks)
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday = weekdays[dt.weekday()]

    lines = []
    lines.append("═" * 40)
    lines.append(f"  📋 今日日报 - {date_str}（{weekday}）")
    lines.append("═" * 40)
    lines.append(f"✅ 完成任务 {totals['total']} 个")
    lines.append("")

    type_order = ["requirement", "bugfix", "review", "tech", "doc", "meeting", "research", "other"]
    for ttype in type_order:
        if ttype not in by_type:
            continue
        type_tasks = by_type[ttype]
        info = TASK_TYPES.get(ttype, {"emoji": "🔧", "label": ttype})
        names = "、".join([t.get("name", "") for t in type_tasks[:3]])
        if len(type_tasks) > 3:
            names += f" 等{len(type_tasks)}项"
        lines.append(f"{info['emoji']} {info['label']}: {names}")

    lines.append("")
    metric_parts = []
    if totals["lines"]: metric_parts.append(f"{fmt_num(totals['lines'])}行")
    if totals["files"]: metric_parts.append(f"{totals['files']}个文件")
    if totals["commits"]: metric_parts.append(f"{totals['commits']}次提交")
    if totals["bugs"]: metric_parts.append(f"修{totals['bugs']}个Bug")
    if totals["reviews"]: metric_parts.append(f"Review{totals['reviews']}次")
    if metric_parts:
        lines.append(f"📊 {' · '.join(metric_parts)}")

    return "\n".join(lines)

# ── 生成周报 ──
def generate_weekly_report(date_str, tasks, start, end):
    by_type, totals = summarize(tasks)

    lines = []
    lines.append(f"# 📋 周报 - {start} ~ {end}")
    lines.append("")
    lines.append(f"> 📌 本周共完成 **{totals['total']}** 个任务")
    lines.append("")

    type_order = ["requirement", "bugfix", "review", "tech", "doc", "meeting", "research", "other"]
    for ttype in type_order:
        if ttype not in by_type:
            continue
        type_tasks = by_type[ttype]
        info = TASK_TYPES.get(ttype, {"emoji": "🔧", "label": ttype})
        lines.append(f"### {info['emoji']} {info['label']}（{len(type_tasks)}）")
        for i, t in enumerate(type_tasks, 1):
            name = t.get("name", "未命名")
            desc = t.get("desc", "")
            lines.append(f"{i}. **{name}**")
            if desc:
                lines.append(f"   - {desc}")
        lines.append("")

    lines.append("## 📊 本周量化数据")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 总任务数 | {totals['total']} |")
    if totals["lines"]: lines.append(f"| 代码/文档行数 | {fmt_num(totals['lines'])} |")
    if totals["files"]: lines.append(f"| 涉及文件数 | {totals['files']} |")
    if totals["commits"]: lines.append(f"| Git Commit | {totals['commits']} |")
    if totals["bugs"]: lines.append(f"| Bug 修复 | {totals['bugs']} |")
    if totals["reviews"]: lines.append(f"| Code Review | {totals['reviews']} |")
    if totals["duration"]: lines.append(f"| 总耗时 | {totals['duration']} 分钟 |")
    lines.append("")

    lines.append("---")
    lines.append(f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    return "\n".join(lines)

# ── 生成月报 ──
def generate_monthly_report(year, month, tasks):
    by_type, totals = summarize(tasks)

    lines = []
    lines.append(f"# 📋 月报 - {year}年{month}月")
    lines.append("")
    lines.append(f"> 📌 本月共完成 **{totals['total']}** 个任务")
    lines.append("")

    type_order = ["requirement", "bugfix", "review", "tech", "doc", "meeting", "research", "other"]
    for ttype in type_order:
        if ttype not in by_type:
            continue
        type_tasks = by_type[ttype]
        info = TASK_TYPES.get(ttype, {"emoji": "🔧", "label": ttype})
        lines.append(f"### {info['emoji']} {info['label']}（{len(type_tasks)}）")
        for i, t in enumerate(type_tasks, 1):
            name = t.get("name", "未命名")
            lines.append(f"{i}. **{name}**")
        lines.append("")

    lines.append("## 📊 本月量化数据")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 总任务数 | {totals['total']} |")
    if totals["lines"]: lines.append(f"| 代码/文档行数 | {fmt_num(totals['lines'])} |")
    if totals["files"]: lines.append(f"| 涉及文件数 | {totals['files']} |")
    if totals["commits"]: lines.append(f"| Git Commit | {totals['commits']} |")
    if totals["bugs"]: lines.append(f"| Bug 修复 | {totals['bugs']} |")
    if totals["reviews"]: lines.append(f"| Code Review | {totals['reviews']} |")
    if totals["duration"]: lines.append(f"| 总耗时 | {totals['duration']} 分钟 |")
    lines.append("")

    lines.append("---")
    lines.append(f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    return "\n".join(lines)

# ── 推送到聊天窗口 ──
def send_report(message, channel="", target=""):
    """调用 notifier.sh 推送消息到聊天窗口（双写：推送 + stdout）"""
    notifier = SCRIPT_DIR / "notifier.sh"
    if not notifier.exists():
        print("⚠️ notifier.sh 不存在，跳过推送", file=sys.stderr)
        return False

    cmd = ["bash", str(notifier), "-m", message]
    if channel:
        cmd += ["--channel", channel]
    if target:
        cmd += ["--target", target]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True
        else:
            print(f"⚠️ 推送失败: {result.stderr}", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("⚠️ 推送超时", file=sys.stderr)
        return False
    except Exception as e:
        print(f"⚠️ 推送异常: {e}", file=sys.stderr)
        return False

# ── 主入口 ──
def main():
    parser = argparse.ArgumentParser(description="赛博牛马日报 — 日报/周报/月报生成器")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="日期 YYYY-MM-DD")
    parser.add_argument("--brief", action="store_true", help="精简版（聊天推送用）")
    parser.add_argument("--week", action="store_true", help="生成周报")
    parser.add_argument("--month", action="store_true", help="生成月报")
    parser.add_argument("--save", action="store_true", default=True, help="保存到文件")
    parser.add_argument("--no-save", dest="save", action="store_false", help="不保存文件")
    parser.add_argument("--send", action="store_true", help="推送到聊天窗口")
    parser.add_argument("--channel", default="", help="推送渠道 (telegram|discord|whatsapp|...)")
    parser.add_argument("--target", default="", help="推送目标 (用户ID/chatID/@username)")
    args = parser.parse_args()

    if args.month:
        dt = datetime.strptime(args.date, "%Y-%m-%d")
        tasks = load_month_tasks(dt.year, dt.month)
        report = generate_monthly_report(dt.year, dt.month, tasks)
        filename = f"{dt.year}-{dt.month:02d}-月报.md"
        print(report)
        if args.save:
            path = REPORT_DIR / filename
            with open(path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n💾 已保存: {path}", file=sys.stderr)
        if args.send:
            send_report(report, args.channel, args.target)

    elif args.week:
        tasks, start, end = load_week_tasks(args.date)
        report = generate_weekly_report(args.date, tasks, start, end)
        filename = f"{start}~{end}-周报.md"
        print(report)
        if args.save:
            path = REPORT_DIR / filename
            with open(path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n💾 已保存: {path}", file=sys.stderr)
        if args.send:
            send_report(report, args.channel, args.target)

    else:
        tasks = load_tasks(args.date)
        if not tasks:
            print(f"📭 {args.date} 暂无任务记录")
            sys.exit(0)

        if args.brief:
            brief = generate_brief(args.date, tasks)
            print(brief)
            if args.send:
                send_report(brief, args.channel, args.target)
        else:
            report = generate_daily_report(args.date, tasks)
            print(report)
            if args.save:
                path = REPORT_DIR / f"{args.date}.md"
                with open(path, "w", encoding="utf-8") as f:
                    f.write(report)
                print(f"\n💾 已保存: {path}", file=sys.stderr)
            if args.send:
                send_report(report, args.channel, args.target)

if __name__ == "__main__":
    main()
