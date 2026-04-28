---
title: 部署与打包
description: 打包为 zip、排除规则、与 Hermes Agent 集成。
date: 2026-04-29
---

# 06 · 部署与打包

## 打包为 zip

```bash
python3 -c "
import zipfile, os, datetime
now = datetime.datetime.now()
suffix = now.strftime('-%m%d-%H%M')
proj_name = 'daily-report' + suffix
base = 'daily-report'
out = f'项目版本/{proj_name}.zip'
os.makedirs('项目版本', exist_ok=True)
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ('data', 'reports')]
        for f in files:
            full = os.path.join(root, f)
            arc = os.path.join(proj_name, os.path.relpath(full, base))
            zf.write(full, arc)
print(f'✅ {out} ({os.path.getsize(out):,} bytes)')
"
```

### 排除项

| 目录 | 原因 |
|------|------|
| `data/` | 运行时数据，每台机器不同 |
| `reports/` | 生成产物，可重新生成 |
| `dev-guide/` | 开发文档，非运行必需 |

## 与 Hermes Agent 集成

Hermes Agent 版使用相同架构，但指标体系不同：

| 维度 | OpenClaw 版 | Hermes 版 |
|------|------------|-----------|
| 任务类型 | 通用 8 类 | 工具体系 12 类 |
| 指标 | 代码行 / 文件数 | Token / 工具调用 / 平台 |
| 配置 | `config-manager.py` | `hermes-config-manager.py` |
| 记录 | `task-tracker.sh` | `hermes-task-tracker.sh` |

### 同时使用两版

```bash
# OpenClaw 版
cd daily-report && bash task-tracker.sh -t doc -n "写文档" --lines 500

# Hermes 版
cd hermes-daily-report && bash hermes-task-tracker.sh -t file -n "写文档" --files-write 1 --tokens-out 2000
```

两版数据完全独立，互不干扰。
