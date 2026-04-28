#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
#  config-manager.py — 配置管理器
#  查看、修改日报系统的所有配置项
# ═══════════════════════════════════════════════════════════════

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "config.json"

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def show_config(cfg):
    print("═" * 50)
    print("  ⚙️  AI 日报系统 — 当前配置")
    print("═" * 50)
    print()

    # Q1: 触发方式
    t = cfg["trigger"]
    modes = {"manual": "手动触发（用户说「日报」才生成）", "auto_count": f"自动计数（{t['auto_count_threshold']}个任务后推送）", "auto_time": f"定时触发（每天 {t['auto_time_hour']}:{t['auto_time_minute']:02d}）"}
    print(f"📌 Q1 触发方式: {modes.get(t['mode'], t['mode'])}")
    print(f"   可选: manual / auto_count / auto_time")
    print()

    # Q2: 推送格式
    s = cfg["report_style"]
    styles = {"brief": f"精简版（最多 {s['brief_max_lines']} 行）", "full": "完整版", "both": "精简版 + 完整版文件"}
    print(f"📋 Q2 推送格式: {styles.get(s['mode'], s['mode'])}")
    print(f"   可选: brief / full / both")
    print()

    # Q3: 任务类型
    tt = cfg["task_types"]
    print(f"🏷️  Q3 任务类型: {tt['mode']}")
    if tt["mode"] == "custom":
        for k, v in tt["types"].items():
            print(f"   {v['emoji']} {v['label']} ({k})")
    else:
        type_set = tt["types"] if tt["mode"] == "preset_8" else tt["preset_4_types"]
        for k, v in type_set.items():
            print(f"   {v['emoji']} {v['label']} ({k})")
    print(f"   可选: preset_8 / preset_4 / custom")
    print()

    # Q4: 提醒
    r = cfg["reminder"]
    remind_modes = {"count": f"计数提醒（每 {r['count_threshold']} 个任务提醒一次）", "always": "每次都提醒", "never": "不提醒"}
    print(f"🔔 Q4 提醒模式: {remind_modes.get(r['mode'], r['mode'])}")
    print(f"   可选: count / always / never")
    if r.get("quiet_hours", {}).get("enabled"):
        print(f"   🌙 免打扰: {r['quiet_hours']['start']} - {r['quiet_hours']['end']}")
    print()

    # Q5: 报告范围
    rs = cfg["report_scope"]
    scope_modes = {"all": "日报 + 周报 + 月报", "daily_only": "仅日报", "daily_weekly": "日报 + 周报"}
    print(f"📅 Q5 报告范围: {scope_modes.get(rs['mode'], rs['mode'])}")
    print(f"   可选: all / daily_only / daily_weekly")
    print()

    # Q6: 消息推送
    notif = cfg.get("notification", {})
    method = notif.get("method", "cli")
    method_labels = {"cli": "CLI 调用（openclaw message send）", "webhook": "Webhook API", "none": "关闭推送"}
    print(f"📡 Q6 消息推送: {method_labels.get(method, method)}")
    print(f"   可选: cli / webhook / none")
    if method == "webhook":
        wh = notif.get("webhook", {})
        print(f"   Webhook URL: {wh.get('url', '未配置')}")
    ch = notif.get("channel", "")
    tgt = notif.get("target", "")
    if ch: print(f"   推送渠道: {ch}")
    if tgt: print(f"   推送目标: {tgt}")
    qh = notif.get("quiet_hours", {})
    if qh.get("enabled"):
        print(f"   🌙 免打扰: {qh.get('start', '23:00')} - {qh.get('end', '08:00')}")
    print()

    print("═" * 50)

def show_help():
    print("""
用法: config-manager.py <命令> [参数]

命令:
  show                              显示当前配置
  set <key> <value>                 修改配置项
  reset                             重置为默认配置
  export                            导出配置（stdout）
  import <json_string>              导入配置

配置键（set 命令可用）:
  trigger.mode                      触发方式 (manual|auto_count|auto_time)
  trigger.auto_count_threshold      自动计数阈值 (数字)
  trigger.auto_time_hour            定时触发-小时 (0-23)
  trigger.auto_time_minute          定时触发-分钟 (0-59)

  report_style.mode                 推送格式 (brief|full|both)
  report_style.brief_max_lines      精简版最大行数 (数字)

  task_types.mode                   任务类型 (preset_8|preset_4|custom)

  reminder.mode                     提醒模式 (count|always|never)
  reminder.count_threshold          计数提醒阈值 (数字)
  reminder.quiet_hours.enabled      免打扰开关 (true|false)
  reminder.quiet_hours.start        免打扰开始 (HH:MM)
  reminder.quiet_hours.end          免打扰结束 (HH:MM)

  report_scope.mode                 报告范围 (all|daily_only|daily_weekly)

  notification.method               推送方式 (cli|webhook|none)
  notification.channel              推送渠道 (telegram|discord|whatsapp|...)
  notification.target               推送目标 (用户ID/chatID/@username)
  notification.webhook.url          Webhook 端点地址
  notification.webhook.token        Webhook 认证 token
  notification.quiet_hours.enabled  免打扰开关 (true|false)
  notification.quiet_hours.start    免打扰开始 (HH:MM)
  notification.quiet_hours.end      免打扰结束 (HH:MM)

示例:
  config-manager.py show
  config-manager.py set trigger.mode auto_count
  config-manager.py set trigger.auto_count_threshold 5
  config-manager.py set report_style.mode full
  config-manager.py set reminder.mode never
  config-manager.py set notification.method cli
  config-manager.py set notification.channel telegram
  config-manager.py set notification.target @myuser
  config-manager.py reset
""")

def set_value(cfg, key, value):
    keys = key.split(".")
    ref = cfg
    for k in keys[:-1]:
        if k not in ref:
            print(f"❌ 未知配置键: {key}")
            return cfg
        ref = ref[k]

    final_key = keys[-1]
    if final_key not in ref:
        print(f"❌ 未知配置键: {key}")
        return cfg

    old_val = ref[final_key]

    # 类型转换
    if isinstance(old_val, bool):
        value = value.lower() in ("true", "1", "yes", "on")
    elif isinstance(old_val, int):
        try:
            value = int(value)
        except ValueError:
            print(f"❌ 值必须是数字: {value}")
            return cfg
    elif isinstance(old_val, float):
        try:
            value = float(value)
        except ValueError:
            print(f"❌ 值必须是数字: {value}")
            return cfg

    ref[final_key] = value
    print(f"✅ {key}: {old_val} → {value}")
    return cfg

def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    cmd = sys.argv[1]
    cfg = load_config()

    if cmd == "show":
        show_config(cfg)

    elif cmd == "set":
        if len(sys.argv) < 4:
            print("❌ 用法: config-manager.py set <key> <value>")
            sys.exit(1)
        key = sys.argv[2]
        value = sys.argv[3]
        cfg = set_value(cfg, key, value)
        save_config(cfg)

    elif cmd == "reset":
        import copy
        default = {
            "_meta": {"version": "1.1.0", "description": "AI 日报系统配置文件 - 所有选项随时可调", "last_modified": "2026-04-29"},
            "trigger": {"mode": "manual", "auto_count_threshold": 5, "auto_time_hour": 23, "auto_time_minute": 0},
            "report_style": {"mode": "brief", "brief_max_lines": 15, "full_save_to_file": True},
            "task_types": cfg["task_types"],
            "reminder": {"mode": "count", "count_threshold": 3, "remind_interval": 0, "quiet_hours": {"enabled": True, "start": "23:00", "end": "08:00"}},
            "report_scope": {"mode": "all", "week_start": "monday", "month_report_day": 1},
            "general": {"data_dir": "data", "report_dir": "reports", "timezone": "Asia/Shanghai", "date_format": "YYYY-MM-DD", "language": "zh-CN", "log_level": "info"},
            "notification": {"method": "cli", "channel": "", "target": "", "webhook": {"url": "http://127.0.0.1:18789/hooks/wake", "token": "", "timeout": 10}, "quiet_hours": {"enabled": True, "start": "23:00", "end": "08:00"}}
        }
        save_config(default)
        print("↩️ 已重置为默认配置")
        show_config(default)

    elif cmd == "export":
        print(json.dumps(cfg, ensure_ascii=False, indent=2))

    elif cmd == "import":
        if len(sys.argv) < 3:
            print("❌ 用法: config-manager.py import '<json>'")
            sys.exit(1)
        try:
            new_cfg = json.loads(sys.argv[2])
            save_config(new_cfg)
            print("✅ 配置已导入")
            show_config(new_cfg)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}")

    elif cmd in ("-h", "--help", "help"):
        show_help()

    else:
        print(f"❌ 未知命令: {cmd}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
