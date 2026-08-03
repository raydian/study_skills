---
name: post-media
description: |-
  This skill should be used when the user wants to publish or upload videos (and optionally
  image-text notes) to Chinese social platforms via the `social-auto-upload` (`sau`) CLI.
  Supports 抖音 (Douyin), 哔哩哔哩 (Bilibili), 小红书 (Xiaohongshu), and 视频号 (Channels,
  experimental). Trigger when the user asks to upload, post, publish, schedule, or batch-upload
  videos to any of these platforms, or to manage platform accounts/cookies.
agent_created: true
---

# post-media

把视频（以及抖音 / 小红书的图文）发布到国内主流社媒平台。本技能是 `social-auto-upload`（简称 `sau`）CLI 的 WorkBuddy 封装，覆盖 **抖音、哔哩哔哩(Bilibili)、小红书** 三条已就绪的命令式上传链路，并提供 **视频号** 的实验性接入说明。

本技能只负责"发布"这一环：确保 `sau` 可用、为每个视频 / 账号生成正确参数、调用命令完成上传。它不负责视频制作（那是 Remotion / subject-videos 等技能的事）。

## 支持平台与能力矩阵

| 平台 | 上传入口 | 视频 | 图文 | 定时 | 状态 |
|------|---------|------|------|------|------|
| 抖音 | `sau douyin` | ✅ | ✅ | ✅ | 就绪 |
| 小红书 | `sau xiaohongshu` | ✅ | ✅ | ✅ | 就绪 |
| Bilibili | `sau bilibili`（自动准备 biliup） | ✅ | ❌ | ✅ | 就绪（强制 `--tid`） |
| 视频号 | `uploader/tencent_uploader`（无 CLI） | ✅ | ✅ | ✅ | ⚠️ 实验性 / 未完成 |

> 视频号在 `social-auto-upload` 中**尚无 `sau` CLI、也无独立 skill**，仅有骨架式 `uploader/tencent_uploader` 与 `examples/upload_video_to_tencent.py`，核心交互方法需手动补全。详见 `references/platform-rules.md` 的「视频号」一节——**不要向用户承诺视频号可一键自动发布**。

## 何时使用

- 用户说"把这条视频发到抖音 / B站 / 小红书""定时发布到小红书""批量上传课程视频"。
- 用户要管理某平台账号的登录态 / cookie（`login` / `check`）。
- 用户要同时向多个平台分发同一视频。

## 前置检查（每次必做）

1. 确认 `sau` 可调用：运行 `sau --help` 或 `uv run sau --help`。不可用见 `references/runtime-requirements.md`。
2. 确认目标账号已登录：`sau <platform> check --account <name>`，输出 `valid` 才继续发布。
3. 登录必须由**用户在本地真实终端**完成（`sau <platform> login --account <name>`）；Agent 不应在非交互 / 沙箱环境硬跑登录。若生成二维码图片，直接把图片展示/发送给用户扫码，不要只回传路径。
4. 用户要求无头 / 有头时显式传 `--headless` / `--headed`；未指定则按平台默认（见各平台规则）。
5. **只当用户明确要求定时发布时才传 `--schedule`**；否则立即发布。

## 各平台规则与约束（重点）

不同平台的上传契约、必填参数、专属限制差异很大，**发布前务必先读对应小节**：

- 抖音 → `references/platform-rules.md` 的「抖音」
- 小红书 → `references/platform-rules.md` 的「小红书」
- Bilibili → `references/platform-rules.md` 的「Bilibili」（强制 `--tid` 分区码）
- 视频号 → `references/platform-rules.md` 的「视频号」（实验性）

精确命令签名（参数名 / 可选项 / 退出码）见 `references/cli-contract.md`。

## 批量发布

需要一次发多条 / 多平台时，用 `scripts/examples/publish_manifest.py` 读取清单 JSON 逐条执行，支持 `--dry-run` 先预览命令：

```bash
/Users/yxy/.workbuddy/binaries/python/versions/3.13.12/bin/python3 \
  <技能目录>/scripts/examples/publish_manifest.py manifest.json --dry-run
/Users/yxy/.workbuddy/binaries/python/versions/3.13.12/bin/python3 \
  <技能目录>/scripts/examples/publish_manifest.py manifest.json --go
```

清单字段与平台差异见脚本内 docstring 与 `references/platform-rules.md`。

## 故障排查

命令失败先看 `references/troubleshooting.md`（`sau` 找不到、cookie 失效、无头二维码、图片限制、频控等）。通用顺序：**先 `check` / `--dry-run`，再 `--go`**。

## 资源

- `references/platform-rules.md` — **四个平台的独立规则与约束说明（核心）**。
- `references/cli-contract.md` — `sau` 三条已就绪平台的精确命令契约。
- `references/runtime-requirements.md` — 安装 `social-auto-upload`、配置 `sau` / patchright / 账号。
- `references/troubleshooting.md` — 常见故障与修复。
- `scripts/examples/publish_manifest.py` — 清单式批量上传。
- `scripts/examples/{douyin,bilibili,xiaohongshu}_commands.sh` — 快速命令模板。
- `scripts/examples/tencent_example.py` — 视频号骨架接入示例（实验性）。
