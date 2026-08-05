#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish.py — 把指定目录下的视频投稿到哔哩哔哩（B 站）

设计目标（与 biliup-rs 配合）：
  - 机械投稿层：扫描目录中的 *.mp4，读取元数据清单（bilibili-manifest.json），
    逐条调用 `biliup` 上传，带封面/标题/标签/简介/分区，条间间隔防频控。
  - 创意层（由 WorkBuddy / LLM 负责，见 SKILL.md）：在运行本脚本前，
    先为每个视频生成标题/标签/简介，必要时用 ImageGen 生成封面，并写入
    bilibili-manifest.json。

用法：
  python3 publish.py <视频目录> [--dry-run | --go]
  python3 publish.py <视频目录> --manifest <清单路径>
  python3 publish.py <视频目录> --extract-covers [--force]   # 提取视频帧作候选封面

参数：
  <视频目录>          必填。包含待发布 .mp4 的目录。
  --manifest PATH    可选。元数据清单 JSON 路径，默认 <视频目录>/bilibili-manifest.json
  --dry-run          只打印将执行的命令，不真正上传（默认）。
  --go               真正投稿（需先登录，存在 ~/.bilibili/cookies.json）。
  --tid N            覆盖分区 tid（默认 201 科学科普）。
  --copyright N      覆盖版权（1=自制，2=转载，默认 1）。
  --tags "a,b,c"     无清单时使用的默认标签（逗号分隔）。
  --prefix TEXT      无清单时，标题前缀（拼到文件名前）。例如 "高中数学必修一："

安全约定：
  - 永远先 --dry-run 确认，再 --go。
  - 固化 unset 代理变量，让 biliup 直连 B 站（避免本机/沙箱代理把 B 站流量送错上游
    导致 "EOF while parsing a value"）。
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request

# ----------------------------------------------------------------------------
# 配置
# ----------------------------------------------------------------------------
BILIUP_DEFAULT = os.path.expanduser("~/bin/biliup")
COOKIE = os.path.expanduser("~/.bilibili/cookies.json")
DEFAULT_TID = 201          # 科技 -> 科学科普
DEFAULT_COPYRIGHT = 1      # 1 = 自制
TITLE_MAX = 80             # B 站标题上限 80 字

# biliup-rs GitHub releases
BILIUP_REPO = "biliup/biliup-rs"
GITHUB_API = "https://api.github.com/repos/%s/releases/latest" % BILIUP_REPO


# ----------------------------------------------------------------------------
# 工具函数
# ----------------------------------------------------------------------------
def log(msg):
    print(msg, flush=True)


def err(msg):
    print("✗ " + msg, file=sys.stderr, flush=True)


def info(msg):
    print("• " + msg, file=sys.stderr, flush=True)


def clean_env():
    """返回一份清掉代理变量的环境，让 biliup 直连 B 站。"""
    env = dict(os.environ)
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
        env.pop(k, None)
    env["NO_PROXY"] = "*"
    env["no_proxy"] = "*"
    return env


def ensure_biliup():
    """确保 biliup 二进制存在；缺失则尝试下载安装，失败则返回 None。"""
    existing = shutil.which("biliup")
    if existing:
        return existing
    if os.path.isfile(BILIUP_DEFAULT):
        return BILIUP_DEFAULT

    info("未找到 biliup，尝试自动下载安装 biliup-rs ...")
    try:
        arch = platform.machine().lower()
        suffix = "aarch64-macos" if arch in ("arm64", "aarch64") else "x86_64-macos"
        with urllib.request.urlopen(GITHUB_API, timeout=30) as r:
            data = json.load(r)
        tag = data.get("tag_name", "")
        asset_name = "biliupR-%s-%s.tar.xz" % (tag, suffix)
        url = None
        for a in data.get("assets", []):
            if a.get("name") == asset_name:
                url = a.get("browser_download_url")
                break
        if not url:
            raise RuntimeError("未找到适配 %s 的发布资产 %s" % (suffix, asset_name))
        os.makedirs(os.path.dirname(BILIUP_DEFAULT), exist_ok=True)
        tmp = "/tmp/biliup_dl.tar.xz"
        urllib.request.urlretrieve(url, tmp)
        import tarfile
        with tarfile.open(tmp) as tf:
            member = next((m for m in tf.getmembers() if m.name.endswith("/biliup")), None)
            if not member:
                raise RuntimeError("压缩包内未找到 biliup 二进制")
            tf.extract(member, "/tmp/biliup_extract")
        src = os.path.join("/tmp/biliup_extract", member.name)
        shutil.move(src, BILIUP_DEFAULT)
        # 移除 macOS 隔离标记（否则 Gatekeeper 会拦截）
        subprocess.run(["xattr", "-d", "com.apple.quarantine", BILIUP_DEFAULT],
                       stderr=subprocess.DEVNULL)
        os.chmod(BILIUP_DEFAULT, 0o755)
        log("✓ 已安装 biliup 到 %s" % BILIUP_DEFAULT)
        return BILIUP_DEFAULT
    except Exception as e:
        err("自动安装 biliup 失败：%s" % e)
        err("请手动安装（二选一）：")
        err("  1) 下载二进制：https://github.com/%s/releases" % BILIUP_REPO)
        err("  2) 或：cargo install biliup  /  brew install biliup")
        err("安装后确保 `biliup` 在 PATH 或位于 %s" % BILIUP_DEFAULT)
        return None


def find_cover(video_path, cover_hint, base_dir):
    """按优先级查找封面图（PNG/JPG）。"""
    candidates = []
    if cover_hint:
        candidates.append(os.path.join(base_dir, cover_hint))
    name = os.path.splitext(os.path.basename(video_path))[0]
    candidates += [
        os.path.join(base_dir, "covers", name + ".png"),
        os.path.join(base_dir, name + ".png"),
        os.path.join(base_dir, name + "_cover.png"),
        os.path.join(base_dir, "covers", name + "_cover.png"),
        os.path.join(base_dir, "covers", name + ".jpg"),
        os.path.join(base_dir, name + ".jpg"),
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None


def detect_ffmpeg():
    """返回 ffmpeg 可执行文件路径；缺失（未安装）返回 None。"""
    p = shutil.which("ffmpeg")
    if p:
        return p
    for cand in ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
        if os.path.isfile(cand):
            return cand
    return None


def extract_frame(video_path, out_path, seek="0", ffmpeg=None):
    """用 ffmpeg 从视频抓取一帧到 out_path。seek 为时间(秒或 hh:mm:ss)。
    成功返回 out_path，失败/无 ffmpeg 返回 None。"""
    if ffmpeg is None:
        ffmpeg = detect_ffmpeg()
    if not ffmpeg:
        return None
    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        # -ss 置于 -i 前可快速定位；-frames:v 1 取单帧；-q:v 2 高画质
        cmd = [ffmpeg, "-y", "-ss", str(seek), "-i", video_path,
               "-frames:v", "1", "-q:v", "2", out_path]
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if os.path.isfile(out_path) and os.path.getsize(out_path) > 0:
            return out_path
        return None
    except Exception:
        return None


def extract_covers(base_dir, manifest, args):
    """--extract-covers 模式：从每支视频提取第一帧(0s) / 第二秒帧(2s) 作为候选封面。

    优先级（与 find_cover 对齐）：先第一帧@0s 作默认封面 covers/<名>.png，
    再第二秒帧@2s 作备选 covers/<名>_t2.png。已存在封面默认跳过，--force 可覆盖。
    """
    ffmpeg = detect_ffmpeg()
    if not ffmpeg:
        err("未找到 ffmpeg，无法提取视频帧。请先 `brew install ffmpeg`；"
            "或跳过此步改用 ImageGen 生成封面（见 metadata_conventions 第 5 节）。")
        return 1
    videos = []
    if manifest:
        for v in manifest.get("videos", []):
            vf = v.get("file")
            vpath = os.path.join(base_dir, vf) if vf else None
            if vpath and os.path.isfile(vpath):
                videos.append(vpath)
    else:
        videos = [os.path.join(base_dir, vf) for vf in scan_videos(base_dir)]
    if not videos:
        err("目录下没有可处理的 .mp4 视频：%s" % base_dir)
        return 1
    for vpath in videos:
        name = os.path.splitext(os.path.basename(vpath))[0]
        cov_dir = os.path.join(base_dir, "covers")
        frame0 = os.path.join(cov_dir, name + ".png")     # 第一帧 @0s（默认封面）
        frame2 = os.path.join(cov_dir, name + "_t2.png")  # 第二秒帧 @2s（备选）
        if os.path.isfile(frame0) and not args.force:
            info("已存在封面，跳过：%s" % frame0)
            continue
        ok0 = extract_frame(vpath, frame0, "0", ffmpeg)
        ok2 = extract_frame(vpath, frame2, "2", ffmpeg)
        if ok0:
            log("✓ 提取第一帧(0s): %s" % frame0)
        if ok2:
            log("✓ 提取第二秒帧(2s): %s" % frame2)
        if not ok0 and not ok2:
            err("✗ 提取失败：%s" % vpath)
    log("提示：用 Read 工具查看 covers/<名>.png；若画面无清晰标题文字，"
        "请用 ImageGen 生成带标题封面并覆盖该文件，再运行 --dry-run / --go。"
        "若第一帧是黑屏/无关，可改用 covers/<名>_t2.png（第二秒帧）覆盖。")
    return 0


def scan_videos(base_dir):
    """列出目录下所有 .mp4（按文件名排序）。"""
    return sorted(
        f for f in os.listdir(base_dir) if f.lower().endswith(".mp4") and os.path.isfile(os.path.join(base_dir, f))
    )


def load_manifest(manifest_path, base_dir):
    if not manifest_path or not os.path.isfile(manifest_path):
        return None
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    log("• 已读取清单：%s（%d 条视频）" % (manifest_path, len(data.get("videos", []))))
    return data


def build_items(base_dir, manifest, args):
    """产出投稿条目列表：[(video_path, title, tags, desc, cover_path), ...]"""
    items = []
    if manifest:
        for v in manifest.get("videos", []):
            vf = v.get("file")
            vpath = os.path.join(base_dir, vf) if vf else None
            if not vpath or not os.path.isfile(vpath):
                err("清单中的视频不存在，跳过：%s" % vf)
                continue
            title = (v.get("title") or os.path.splitext(os.path.basename(vpath))[0])[:TITLE_MAX]
            tags = v.get("tags") or []
            desc = v.get("desc") or ""
            cover = find_cover(vpath, v.get("cover"), base_dir)
            items.append((vpath, title, tags, desc, cover))
        return items

    # 无清单：按文件名兜底
    info("未找到 bilibili-manifest.json，按文件名兜底生成元数据。")
    default_tags = [t.strip() for t in (args.tags or "Bilibili").split(",") if t.strip()]
    prefix = args.prefix or ""
    for vf in scan_videos(base_dir):
        vpath = os.path.join(base_dir, vf)
        base = os.path.splitext(vf)[0]
        title = (prefix + base)[:TITLE_MAX]
        cover = find_cover(vpath, None, base_dir)
        items.append((vpath, title, default_tags, "", cover))
    return items


def publish_one(biliup, cookie, item, tid, copyright_val, go):
    vpath, title, tags, desc, cover = item
    args = [biliup, "-u", cookie, "upload", vpath,
            "--title", title, "--tid", str(tid), "--copyright", str(copyright_val),
            "--tag", ",".join(tags), "--desc", desc]
    if cover:
        args += ["--cover", cover]

    log("  标题 : %s" % title)
    log("  标签 : %s" % ",".join(tags))
    if cover:
        log("  封面 : %s" % cover)
    else:
        log("  封面 : (无，未找到封面文件)")
    if not go:
        log("  (dry-run) " + " ".join(args))
        return True

    log("  投稿中 ...")
    try:
        out = subprocess.run(args, env=clean_env(), capture_output=True, text=True, timeout=600)
        sys.stdout.write(out.stdout)
        if out.stderr:
            sys.stderr.write(out.stderr)
        ok = out.returncode == 0 and ("code:0" in out.stdout or "已提交" in out.stdout or "投稿成功" in out.stdout)
        if ok:
            log("  ✓ 已提交")
        else:
            err("  ✗ 上传返回非预期（rc=%s）。若报 EOF/connection reset，"
                "多为 WorkBuddy 沙箱或本机代理拦截 B 站，请改在独立终端运行本脚本。" % out.returncode)
        return ok
    except subprocess.TimeoutExpired:
        err("  ✗ 上传超时（>600s）")
        return False


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="把目录下的视频投稿到 B 站")
    ap.add_argument("directory", help="包含待发布 .mp4 的目录")
    ap.add_argument("--manifest", help="元数据清单 JSON 路径")
    ap.add_argument("--dry-run", action="store_true", help="只打印命令不真发（默认）")
    ap.add_argument("--go", action="store_true", help="真正投稿")
    ap.add_argument("--tid", type=int, default=None, help="分区 tid")
    ap.add_argument("--copyright", type=int, default=None, help="版权 1=自制 2=转载")
    ap.add_argument("--tags", default=None, help="无清单时的默认标签(a,b,c)")
    ap.add_argument("--prefix", default=None, help="无清单时标题前缀")
    ap.add_argument("--extract-covers", action="store_true",
                    help="从视频提取第一帧(0s)/第二秒帧(2s)作为候选封面（需 ffmpeg）")
    ap.add_argument("--force", action="store_true",
                    help="--extract-covers 时覆盖已存在的封面帧")
    args = ap.parse_args()

    go = args.go and not args.dry_run
    base_dir = os.path.abspath(args.directory)
    if not os.path.isdir(base_dir):
        err("目录不存在：%s" % base_dir)
        sys.exit(1)

    # 0) 仅提取封面帧（不需要 biliup / 登录态）
    if args.extract_covers:
        manifest_path = args.manifest or os.path.join(base_dir, "bilibili-manifest.json")
        rc = extract_covers(base_dir, load_manifest(manifest_path, base_dir), args)
        sys.exit(rc)

    # 1) 二进制
    biliup = ensure_biliup()
    if not biliup:
        sys.exit(1)

    # 2) 登录态
    if go and not os.path.isfile(COOKIE):
        err("尚未登录。请在【独立终端】（macOS 终端.app / iTerm，不在 WorkBuddy 内）运行：")
        err("  %s -u %s login" % (biliup, COOKIE))
        err("选「扫码登录」→ 手机 B 站 App 扫码确认 → 生成 %s" % COOKIE)
        sys.exit(1)

    # 3) 清单与条目
    manifest_path = args.manifest or os.path.join(base_dir, "bilibili-manifest.json")
    manifest = load_manifest(manifest_path, base_dir)
    tid = args.tid if args.tid is not None else (manifest.get("tid", DEFAULT_TID) if manifest else DEFAULT_TID)
    copyright_val = args.copyright if args.copyright is not None else (manifest.get("copyright", DEFAULT_COPYRIGHT) if manifest else DEFAULT_COPYRIGHT)

    items = build_items(base_dir, manifest, args)
    if not items:
        err("目录下没有可发布的 .mp4 视频：%s" % base_dir)
        sys.exit(1)

    log("=" * 60)
    log("模式: %s   分区 tid=%s   版权=%s" % ("GO" if go else "DRY-RUN", tid, copyright_val))
    log("目录: %s" % base_dir)
    log("视频数: %d" % len(items))
    log("=" * 60)

    ok_count = 0
    for idx, item in enumerate(items, 1):
        log("\n[%d/%d]" % (idx, len(items)))
        if publish_one(biliup, COOKIE, item, tid, copyright_val, go):
            ok_count += 1
        if go and idx < len(items):
            time.sleep(3)  # 防连续投稿触发频控（code 601 上传过快）

    log("\n" + "=" * 60)
    if go:
        log("完成：成功 %d / 共 %d" % (ok_count, len(items)))
        if ok_count < len(items):
            err("有 %d 条未成功，请检查上方错误。" % (len(items) - ok_count))
    else:
        log("以上为 DRY-RUN。确认无误后运行：")
        log("  python3 %s %s --go" % (os.path.abspath(__file__), base_dir))


if __name__ == "__main__":
    main()
