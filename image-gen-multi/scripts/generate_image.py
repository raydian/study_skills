#!/usr/bin/env python3
"""image-gen-multi 统一生图入口。

多渠道生图技能的核心脚本：把文生图 / 图生图请求路由到
foxcode（OpenAI 兼容三方）/ 千问百炼（bl）/ 火山引擎（arkcli）三个渠道之一，
产物统一落盘并输出 manifest。

用法示例：
    python3 generate_image.py --prompt "一只柴犬在樱花树下" --size 16:9
    python3 generate_image.py --provider foxcode --prompt "赛博朋克城市" --size 1536x1024 --quality high
    python3 generate_image.py --provider bailian --prompt "山水画" --size 16:9 --watermark false
    python3 generate_image.py --provider volcengine --prompt "未来城市海报"
    python3 generate_image.py --prompt "把背景改成星空" --input-image ./input.png

渠道优先级（auto）：foxcode → volcengine(arkcli) → bailian(bl)
"""

import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ---------- 常量 ----------

FOXCODE_BASE_URL = os.environ.get("FOX_CODE_BASE_URL", "https://dm-fox.rjj.cc/codex/v1")
FOXCODE_DEFAULT_MODEL = os.environ.get("FOX_CODE_DEFAULT_MODEL", "gpt-image-2")
FOXCODE_KEY = os.environ.get("FOX_CODE_API_KEY", "")

BAILIAN_DEFAULT_MODEL = "qwen-image-3.0"
VOLCENGINE_DEFAULT_MODEL = os.environ.get("ARK_DEFAULT_MODEL", "doubao-seedream-4-5-251128")

# auto 降级顺序（2026-08-16 定稿）
AUTO_ORDER = ["foxcode", "volcengine", "bailian"]


# ---------- 工具函数 ----------

def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def run_cmd(cmd: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    """运行外部命令，超时报错。"""
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        fail(f"命令超时（{timeout}s）: {' '.join(cmd)}")
    except FileNotFoundError:
        fail(f"命令不存在: {cmd[0]}")


def download_url(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "image-gen-multi/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        shutil.copyfileobj(resp, f)


def save_bytes(data: bytes, dest: Path) -> None:
    dest.write_bytes(data)


def write_manifest(meta: dict, out_dir: Path) -> Path:
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path


def ensure_out_dir(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)


def make_filename(prefix: str, idx: int, ext: str, ts: str) -> str:
    return f"{prefix}_{idx}_{ts}.{ext}"


def pick_ext(url: str, default: str = "png") -> str:
    if url:
        low = url.lower().split("?")[0]
        for cand in (".png", ".jpg", ".jpeg", ".webp"):
            if low.endswith(cand):
                return cand.lstrip(".")
    return default


# ---------- 渠道：foxcode（OpenAI 兼容） ----------

def foxcode_generate(args) -> dict:
    if not FOXCODE_KEY:
        fail("FOX_CODE_API_KEY 未设置，无法使用 foxcode 渠道")

    model = args.model or FOXCODE_DEFAULT_MODEL
    body = {
        "model": model,
        "prompt": args.prompt,
        "n": args.n,
    }
    if args.size:
        body["size"] = args.size
    if args.quality:
        body["quality"] = args.quality

    # 图生图：OpenAI 兼容 image 字段（base64）
    if args.input_image:
        with open(args.input_image, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        body["image"] = f"data:image/png;base64,{b64}"

    url = f"{FOXCODE_BASE_URL}/images/generations"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {FOXCODE_KEY}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:500] if e.fp else str(e)
        fail(f"foxcode HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        fail(f"foxcode 网络错误: {e.reason}")

    items = data.get("data") or []
    if not items:
        fail(f"foxcode 返回空结果: {json.dumps(data, ensure_ascii=False)[:500]}")

    return {"items": items, "model": model, "provider": "foxcode"}


# ---------- 渠道：千问百炼（bl CLI） ----------

def bailian_generate(args) -> dict:
    if not shutil.which("bl"):
        fail("bl CLI 未安装（bailian-cli），无法使用千问百炼渠道")

    ts = time.strftime("%Y%m%d%H%M%S")
    out_dir = Path(args.out_dir)
    ensure_out_dir(out_dir)
    prefix = args.out_prefix

    if args.input_image:
        # 图生图：bl image edit
        cmd = ["bl", "image", "edit", "--image", str(args.input_image)]
        cmd += ["--prompt", args.prompt]
        if args.model:
            cmd += ["--model", args.model]
        if args.size:
            cmd += ["--size", args.size]
        if args.n:
            cmd += ["--n", str(args.n)]
        if args.seed is not None:
            cmd += ["--seed", str(args.seed)]
        if args.negative_prompt:
            cmd += ["--negative-prompt", args.negative_prompt]
        if args.watermark is not None:
            cmd += ["--watermark", str(args.watermark).lower()]
        cmd += ["--out-dir", str(out_dir)]
        cmd += ["--out-prefix", args.out_prefix]
    else:
        # 文生图
        cmd = ["bl", "image", "generate", "--prompt", args.prompt]
        cmd += ["--model", args.model or BAILIAN_DEFAULT_MODEL]
        if args.size:
            cmd += ["--size", args.size]
        if args.n:
            cmd += ["--n", str(args.n)]
        if args.seed is not None:
            cmd += ["--seed", str(args.seed)]
        if args.negative_prompt:
            cmd += ["--negative-prompt", args.negative_prompt]
        if args.watermark is not None:
            cmd += ["--watermark", str(args.watermark).lower()]
        cmd += ["--out-dir", str(out_dir)]
        cmd += ["--out-prefix", prefix]

    log(f"[bailian] {' '.join(cmd)}")
    proc = run_cmd(cmd, timeout=args.timeout)
    if proc.returncode != 0:
        fail(f"bl 调用失败: {proc.stderr[-800:]}")

    # bl 已自动下载到 out-dir，收集产物
    files = sorted(out_dir.glob(f"{prefix}_*")) if out_dir.exists() else []
    if not files:
        # 兼容 bl 自定义前缀输出
        files = sorted(out_dir.glob("*.png")) + sorted(out_dir.glob("*.jpg")) + sorted(out_dir.glob("*.jpeg"))
    return {
        "items": [{"local_path": str(p)} for p in files],
        "model": args.model or BAILIAN_DEFAULT_MODEL,
        "provider": "bailian",
        "raw_output": proc.stdout[-500:],
    }


# ---------- 渠道：火山引擎（arkruntime API 直调为主，arkcli 兜底） ----------

# arkruntime 端点（Seedream 系列，OpenAI 兼容）
VOLCENGINE_API_BASE = os.environ.get("ARK_API_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
VOLCENGINE_API_KEY = os.environ.get("ARK_API_KEY", "")
# 兜底：从 arkcli 配置读取 platform profile 的 API key（本机已配置时）
_ARKCLI_CONFIG = Path.home() / ".arkcli" / "config.yaml"


def _arkcli_config_key() -> str:
    """从 ~/.arkcli/config.yaml 提取 platform profile 的 api_key（兜底鉴权）。"""
    try:
        import yaml  # 延迟导入，非必需依赖

        cfg = yaml.safe_load(_ARKCLI_CONFIG.read_text(encoding="utf-8")) if _ARKCLI_CONFIG.exists() else {}
        for prof in (cfg.get("profiles") or {}).values():
            if prof.get("type") == "platform" and prof.get("api_key"):
                return prof["api_key"]
    except Exception:
        pass
    return ""


def volcengine_generate(args) -> dict:
    """火山引擎：优先 ARK_API_KEY 直调 arkruntime（已验证可用），否则走 arkcli。"""
    key = VOLCENGINE_API_KEY or _arkcli_config_key()

    if key:
        return _volcengine_api_direct(args, key)

    if shutil.which("arkcli"):
        return _volcengine_arkcli(args)

    fail("火山引擎渠道不可用：未设置 ARK_API_KEY 且 arkcli 未安装/未配置")


def _volcengine_api_direct(args, key: str) -> dict:
    """ARK_API_KEY 直调 arkruntime /images/generations（OpenAI 兼容）。"""
    model = args.model or VOLCENGINE_DEFAULT_MODEL
    body = {
        "model": model,
        "prompt": args.prompt,
        "n": args.n,
    }
    # Seedream 系列要求像素尺寸 ≥ 约 2K（3686400 像素）；比例换算为对应像素
    if args.size:
        body["size"] = _size_to_ark(args.size)
    else:
        body["size"] = "2048x2048"

    if args.input_image:
        with open(args.input_image, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        body["image"] = f"data:image/png;base64,{b64}"

    url = f"{VOLCENGINE_API_BASE}/images/generations"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=max(args.timeout, 300)) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:500] if e.fp else str(e)
        fail(f"volcengine HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        fail(f"volcengine 网络错误: {e.reason}")

    items = data.get("data") or []
    if not items:
        fail(f"volcengine 返回空结果: {json.dumps(data, ensure_ascii=False)[:500]}")

    return {"items": items, "model": model, "provider": "volcengine"}


def _size_to_ark(size: str) -> str:
    """统一尺寸换算为 arkruntime 像素尺寸（Seedream 4.5 要求 ≥ 3686400 像素）。"""
    ratio_map = {
        "1:1": "2048x2048",
        "16:9": "2560x1440",
        "9:16": "1440x2560",
        "3:4": "2048x2732",
        "4:3": "2732x2048",
        "21:9": "2688x1152",
        "2k": "2048x2048",
        "4k": "4096x4096",
    }
    s = size.lower()
    if s in ratio_map:
        return ratio_map[s]
    if "x" in s:
        return s
    return "2048x2048"


def _volcengine_arkcli(args) -> dict:
    """arkcli +gen 路径（需要 agent-plan profile 或已部署 endpoint）。"""
    ts = time.strftime("%Y%m%d%H%M%S")
    out_dir = Path(args.out_dir)
    ensure_out_dir(out_dir)
    prefix = args.out_prefix

    cmd = ["arkcli", "+gen", args.prompt]
    if args.model:
        cmd += ["--model", args.model]
    if args.n and args.n > 1:
        cmd += ["--n", str(args.n)]
    if args.seed is not None:
        cmd += ["--seed", str(args.seed)]
    if args.size:
        # 兼容比例（16:9）或像素（1024x1024），arkcli 用 --ratio / --resolution
        if ":" in args.size:
            cmd += ["--ratio", args.size]
        else:
            cmd += ["--resolution", args.size]
    if args.input_image:
        cmd += ["--input", f"@{args.input_image}"]
    cmd += ["--save-to", str(out_dir)]
    cmd += ["--no-open"]

    log(f"[volcengine] {' '.join(cmd)}")
    proc = run_cmd(cmd, timeout=max(args.timeout, 600))
    if proc.returncode != 0:
        fail(f"arkcli 调用失败: {proc.stderr[-800:]}")

    # arkcli 已用 --save-to 保存到 out-dir，收集产物
    files = sorted(out_dir.glob(f"{prefix}_*")) if out_dir.exists() else []
    if not files:
        files = (
            sorted(out_dir.glob("*.png"))
            + sorted(out_dir.glob("*.jpg"))
            + sorted(out_dir.glob("*.jpeg"))
            + sorted(out_dir.glob("*.webp"))
        )
    if not files:
        fail(f"arkcli 未找到产物，输出片段: {(proc.stdout + proc.stderr)[-500:]}")

    return {
        "items": [{"local_path": str(p)} for p in files],
        "model": args.model or VOLCENGINE_DEFAULT_MODEL,
        "provider": "volcengine",
        "raw_output": (proc.stdout + proc.stderr)[-500:],
    }


# ---------- 探测 ----------

def check_foxcode() -> bool:
    return bool(FOXCODE_KEY)


def check_volcengine() -> bool:
    # ARK_API_KEY 直调 或 arkcli 已登录，任一可用即可
    if VOLCENGINE_API_KEY or _arkcli_config_key():
        return True
    if not shutil.which("arkcli"):
        return False
    proc = run_cmd(["arkcli", "auth", "status"], timeout=60)
    return proc.returncode == 0 and "sso" in (proc.stdout + proc.stderr).lower()


def check_bailian() -> bool:
    return bool(shutil.which("bl"))


def resolve_provider(args) -> str:
    if args.provider != "auto":
        return args.provider
    for name in AUTO_ORDER:
        ok = {
            "foxcode": check_foxcode,
            "volcengine": check_volcengine,
            "bailian": check_bailian,
        }[name]()
        if ok:
            return name
    fail("所有渠道均不可用：请检查 FOX_CODE_API_KEY / arkcli 登录 / bl 安装")


# ---------- 产物落盘 ----------

def finalize(provider_result: dict, args) -> Path:
    ts = time.strftime("%Y%m%d%H%M%S")
    out_dir = Path(args.out_dir)
    ensure_out_dir(out_dir)
    prefix = args.out_prefix
    saved = []

    for idx, item in enumerate(provider_result["items"]):
        if item.get("local_path"):
            p = Path(item["local_path"])
            if p.exists() and p.parent != out_dir:
                # 拷贝到 out-dir
                target = out_dir / p.name
                if target.exists() and target.resolve() != p.resolve():
                    target = out_dir / make_filename(prefix, idx, p.suffix.lstrip("."), ts)
                shutil.copy2(p, target)
                saved.append(str(target))
            else:
                saved.append(str(p))
            continue

        b64 = item.get("b64_json")
        url = item.get("url")
        if b64:
            ext = "png"
            target = out_dir / make_filename(prefix, idx, ext, ts)
            save_bytes(base64.b64decode(b64), target)
            saved.append(str(target))
        elif url:
            ext = pick_ext(url)
            target = out_dir / make_filename(prefix, idx, ext, ts)
            download_url(url, target)
            saved.append(str(target))

    if not saved:
        fail("未生成任何图片文件")

    manifest = {
        "provider": provider_result["provider"],
        "model": provider_result["model"],
        "prompt": args.prompt,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "files": saved,
    }
    if args.input_image:
        manifest["input_image"] = args.input_image
    if provider_result.get("raw_output"):
        manifest["provider_output"] = provider_result["raw_output"]

    manifest_path = write_manifest(manifest, out_dir)
    return manifest_path


# ---------- 主流程 ----------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="image-gen-multi 多渠道生图统一入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "渠道优先级（auto）：foxcode → volcengine(arkcli) → bailian(bl)\n"
            "示例：\n"
            "  python3 generate_image.py --prompt '一只柴犬在樱花树下' --size 16:9\n"
            "  python3 generate_image.py --provider foxcode --prompt '赛博朋克城市' --quality high\n"
            "  python3 generate_image.py --provider bailian --prompt '山水画' --watermark false\n"
            "  python3 generate_image.py --provider volcengine --prompt '未来城市海报'\n"
            "  python3 generate_image.py --prompt '把背景改成星空' --input-image ./input.png"
        ),
    )
    parser.add_argument("--provider", choices=["auto", "foxcode", "bailian", "volcengine"], default="auto")
    parser.add_argument("--prompt", default=None, help="图像描述 / 编辑指令（dry-run 可省略）")
    parser.add_argument("--model", default=None, help="渠道模型 ID（默认按渠道）")
    parser.add_argument("--size", default=None, help="尺寸：16:9 / 1024x1024 / 1536x1024 / 2K 等")
    parser.add_argument("--quality", choices=["low", "medium", "high", "auto"], default=None, help="质量档位（foxcode）")
    parser.add_argument("--n", type=int, default=1, help="生成张数（默认 1）")
    parser.add_argument("--seed", type=int, default=None, help="随机种子（渠道支持时）")
    parser.add_argument("--negative-prompt", default=None, help="负面提示（渠道支持时）")
    parser.add_argument("--watermark", type=lambda s: s.lower() in ("true", "1", "yes"), default=None, help="是否加水印（bailian，true/false）")
    parser.add_argument("--input-image", default=None, help="参考图路径（提供则为图生图/编辑）")
    parser.add_argument("--out-dir", default="./output", help="产物输出目录（默认 ./output）")
    parser.add_argument("--out-prefix", default="image", help="文件名前缀（默认 image）")
    parser.add_argument("--fallback", action="store_true", default=True, help="失败时按优先级切换渠道（默认开启）")
    parser.add_argument("--no-fallback", dest="fallback", action="store_false", help="关闭渠道降级")
    parser.add_argument("--timeout", type=int, default=300, help="请求超时秒数（默认 300）")
    parser.add_argument("--json", action="store_true", help="输出 manifest 路径（JSON 单行）")
    parser.add_argument("--dry-run", action="store_true", help="只探测渠道，不真正生图")
    args = parser.parse_args()

    if args.dry_run:
        for name in AUTO_ORDER:
            ok = {
                "foxcode": check_foxcode,
                "volcengine": check_volcengine,
                "bailian": check_bailian,
            }[name]()
            print(f"{name}: {'可用' if ok else '不可用'}")
        return

    if not args.prompt:
        parser.error("--prompt 必填（dry-run 除外）")

    provider = resolve_provider(args)
    log(f"[auto/指定] 使用渠道: {provider}")

    attempts = []
    order = [provider]
    if args.fallback:
        order = AUTO_ORDER[AUTO_ORDER.index(provider):] if provider in AUTO_ORDER else [provider]

    for name in order:
        try:
            result = {
                "foxcode": foxcode_generate,
                "bailian": bailian_generate,
                "volcengine": volcengine_generate,
            }[name](args)
            manifest_path = finalize(result, args)
            attempts.append(name)
            if args.json:
                print(json.dumps({"provider": name, "manifest": str(manifest_path)}, ensure_ascii=False))
            else:
                print(f"OK: 渠道={name} 模型={result['model']}")
                print(f"产物: {str(manifest_path)}")
            return
        except SystemExit as e:
            attempts.append(name)
            if not args.fallback or name == order[-1]:
                raise
            log(f"[降级] 渠道 {name} 失败，尝试下一渠道")
            continue

    fail("所有渠道均失败")


if __name__ == "__main__":
    main()
