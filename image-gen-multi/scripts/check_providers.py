#!/usr/bin/env python3
"""image-gen-multi 渠道可用性探测。

检查三个生图渠道是否就绪，输出状态表。
auto 模式优先级：foxcode → volcengine(arkcli) → bailian(bl)

用法：
    python3 check_providers.py          # 输出人类可读状态
    python3 check_providers.py --json   # 输出 JSON
"""

import argparse
import json
import os
import shutil
import subprocess
import sys


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def run_cmd(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        proc = subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr="")
        return proc


def check_foxcode() -> tuple[bool, str]:
    key = os.environ.get("FOX_CODE_API_KEY", "")
    base = os.environ.get("FOX_CODE_BASE_URL", "https://dm-fox.rjj.cc/codex/v1")
    if not key:
        return False, "FOX_CODE_API_KEY 未设置"
    if key == "sk-xxxx" or key.startswith("sk-ant-oat01-"):
        return True, f"已设置（{base}，模型 gpt-image-2）"
    return True, f"已设置（{base}，模型 gpt-image-2）"


def check_bailian() -> tuple[bool, str]:
    bl_path = shutil.which("bl")
    if not bl_path:
        return False, "bl CLI 未安装"
    proc = run_cmd(["bl", "--version"])
    version = (proc.stdout + proc.stderr).strip().splitlines()[0] if proc.returncode == 0 else "unknown"
    # 鉴权探测：bl auth status 属于协议类命令，这里仅确认 CLI 可用
    return True, f"bl {version} 可用（{bl_path}）"


def check_volcengine() -> tuple[bool, str]:
    key = os.environ.get("ARK_API_KEY", "")
    arkcli_path = shutil.which("arkcli")
    if key:
        return True, "ARK_API_KEY 已设置（直调 arkruntime）"
    if arkcli_path:
        proc = run_cmd(["arkcli", "auth", "status"])
        out = proc.stdout + proc.stderr
        if proc.returncode == 0 and "sso" in out.lower():
            return True, "arkcli 已 SSO 登录"
        return False, "arkcli 未登录（运行 arkcli auth login volc-sso）"
    # 兜底：arkcli 配置文件中的 platform key
    cfg_path = os.path.expanduser("~/.arkcli/config.yaml")
    if os.path.exists(cfg_path):
        try:
            import yaml
            cfg = yaml.safe_load(open(cfg_path, encoding="utf-8"))
            for prof in (cfg.get("profiles") or {}).values():
                if prof.get("type") == "platform" and prof.get("api_key"):
                    return True, "从 arkcli 配置读取到 platform API key"
        except Exception:
            pass
    return False, "无 ARK_API_KEY，arkcli 未安装/未配置"


def main() -> None:
    parser = argparse.ArgumentParser(description="image-gen-multi 渠道可用性探测")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    checks = [
        ("foxcode", check_foxcode()),
        ("volcengine", check_volcengine()),
        ("bailian", check_bailian()),
    ]

    if args.json:
        print(json.dumps({name: {"available": ok, "detail": detail} for name, (ok, detail) in checks}, ensure_ascii=False, indent=2))
        return

    print(f"{'渠道':<12} {'状态':<6} 说明")
    print("-" * 60)
    for name, (ok, detail) in checks:
        status = "可用" if ok else "不可用"
        print(f"{name:<12} {status:<6} {detail}")

    auto_order = ["foxcode", "volcengine", "bailian"]
    chosen = next((n for n in auto_order if dict(checks)[n][0]), None)
    print("-" * 60)
    if chosen:
        print(f"auto 模式将优先使用: {chosen}")
    else:
        print("所有渠道均不可用")


if __name__ == "__main__":
    main()
