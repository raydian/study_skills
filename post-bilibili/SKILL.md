---
name: post-bilibili
description: |-
  This skill should be used when the user wants to publish or batch-upload video files from a
  specified directory to Bilibili (哔哩哔哩). It ensures the biliup-rs uploader is installed and
  logged in, generates titles / tags / descriptions / covers for each video, and submits them to
  Bilibili with proper rate-limiting. Trigger when the user asks to upload, post, publish, or
  投稿 videos to Bilibili, or to batch-publish a folder of course / lecture videos.
agent_created: true
---

# post-bilibili

把指定目录下的视频发布到哔哩哔哩（B 站）。本技能负责"投稿"这一环节：确保上传工具就绪、
为每个视频生成标题/标签/简介/封面、并逐条提交到 B 站。它不负责视频本身的制作（那是
Remotion / subject-videos 等技能的事）。

## 何时使用

- 用户说"把这目录的视频发到 B 站""投稿这几个视频""批量上传课程视频到哔哩哔哩"。
- 视频已存在于某目录（如 `video/数学/4.2-指数函数-五讲重制版/output/`），需要带标题、标签、
  简介、封面发布。

## 核心流程

### 第 0 步：确认输入目录

向用户确认（或读取）目标目录，该目录下应含 `.mp4` 文件，可选含 `covers/` 封面子目录。
若该目录无任何 `.mp4`，先反馈再继续。

### 第 1 步：确保 biliup-rs 就绪

`scripts/publish.py` 在运行时会自动检测并（尝试）安装 `biliup`；但**登录必须人工完成**：

- **登录无法由 Agent 代劳**：扫码是交互式 TUI，且 WorkBuddy 沙箱会拦截 B 站（见
  `references/biliup_reference.md` 第 5.2 节）。必须在用户本机的**独立终端**（macOS 终端.app
  / iTerm，不在 WorkBuddy 内）执行：
  ```bash
  ~/bin/biliup -u ~/.bilibili/cookies.json login
  ```
  选「扫码登录」→ 手机 B 站 App 扫码确认。
- **检查登录态**：若 `~/.bilibili/cookies.json` 不存在，直接告诉用户上面的命令并请其登录；
  不要尝试自行登录。登录完成后继续。

### 第 2 步：为每个视频生成元数据

读取 `references/metadata_conventions.md` 作为规范，为目录中每个 `.mp4` 生成：

- **标题**（≤80 字，推荐 `高中数学必修一：<章节>-<序号>-<主题>｜知识点讲解` 结构）
- **标签**（3–8 个，大词+长尾词）
- **简介**（纯文本，写明本节内容与适用人群）
- **封面**：若 `covers/<名>.png` 已存在则直接用；否则用 WorkBuddy 内置 **ImageGen** 工具
  生成一张宽屏知识封面，保存到 `covers/<视频名>.png`（提示词模板见 metadata_conventions 第 5 节）。

将结果写入 `<目录>/bilibili-manifest.json`，格式见 `references/metadata_conventions.md` 第 1 节。
**质量优先**：标题/标签/简介决定了检索与点击，值得认真写，不要只拿文件名凑数。

### 第 3 步：Dry-run 校验

运行（用受管 Python）：
```bash
/Users/yxy/.workbuddy/binaries/python/versions/3.13.12/bin/python3 \
  <技能目录>/scripts/publish.py "<目录>" --dry-run
```
确认脚本正确识别了每条视频、封面、标题、标签、简介，无"缺失"警告。若有缺失，回去补元数据或封面。

### 第 4 步：正式投稿

```bash
/Users/yxy/.workbuddy/binaries/python/versions/3.13.12/bin/python3 \
  <技能目录>/scripts/publish.py "<目录>" --go
```

- 脚本会自动 `unset` 代理变量让 biliup 直连 B 站（规避 `EOF while parsing a value`）。
- 条间 `sleep 3` 防频控（`code 601 上传过快`）。
- **若在本步骤报 EOF / connection reset**：说明 WorkBuddy 沙箱仍在拦截 B 站。请用户在独立终端
  运行同一条 `publish.py --go` 命令（脚本本身已固化代理处理，无需额外参数）。

### 第 5 步：回收结果

- 每条成功会打印 `✓ 已提交` 并返回 BV 号（如 `BV13iK86QEMh`）。
- 稿件进入 B 站**审核队列**，审核通过后公开可见。
- 建议把 BV 号 + 链接整理进目录内的投稿记录（如 `bilibili-upload.md`），方便追溯。

## 关键注意

- **永远先 `--dry-run` 再 `--go`**。
- **登录与（必要时）上传需在 WorkBuddy 之外的独立终端完成**——这是本技能最重要的环境约束，
  详见 `references/biliup_reference.md`。
- 标题超 80 字会被 B 站截断，`publish.py` 已做截断保护。
- 新号连续投稿可能触发 `code 601`，等几分钟重跑即可，非脚本故障。

## 资源

- `scripts/publish.py` — 通用投稿脚本（扫描目录、读清单、逐条上传、代理处理、频控）。
- `references/biliup_reference.md` — biliup-rs 安装/登录/命令/分区码/踩坑全集。
- `references/metadata_conventions.md` — 标题/标签/简介/封面生成规范与 ImageGen 提示词模板。
