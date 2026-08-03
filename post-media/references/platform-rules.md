# 各平台独立规则与约束说明

本文件对 `post-media` 支持的四个平台分别给出**发布规则、必填 / 可选参数、专属限制与风险点**。发布前按目标平台阅读对应小节。

---

## 抖音（Douyin）

**入口命令**：`sau douyin`

### 动作与命令

| 动作 | 命令 |
|------|------|
| 登录 | `sau douyin login --account <name>` |
| 校验 cookie | `sau douyin check --account <name>` |
| 上传视频 | `sau douyin upload-video ...` |
| 上传图文 | `sau douyin upload-note ...` |

### 必填 / 可选参数

- **upload-video** 必填：`--account` `--file` `--title`
  可选：`--desc` `--tags`（逗号分隔） `--schedule "YYYY-MM-DD HH:MM"` `--thumbnail` `--product-link` `--product-title` `--debug` `--headless` / `--headed`
- **upload-note** 必填：`--account` `--images`（多张） `--title`
  可选：`--note` `--tags` `--schedule` `--debug` `--headless` / `--headed`

### 约束

1. `upload-video` 每次命令**仅支持一个视频文件**。
2. `upload-note` 每次命令支持**多张图片**，当前**最多 35 张，且不支持 GIF**。
3. 视频描述统一用 `--desc`；图文正文统一用 `--note`。
4. `--schedule` 时间格式固定 `YYYY-MM-DD HH:MM`；**不传即立即发布**。
5. **二次验证**：抖音触发短信 2FA 时，CLI 优先读取项目根目录 `verify_code.txt`；若在本地交互终端运行，也可按提示直接输入验证码。
6. **账号约定**：`--account` 是用户自定义的 `account_name`（非固定 `creator`）；一个 `account_name` 对应一个账号文件，可多账号隔离与并发。
7. **运行模式**：用户未指定时，不要强行加 `--headless` / `--headed`；仅当用户明确要求时显式传入。
8. **元数据约定**：视频 = `title + desc + tags`；图文 = `title + note + tags`。

---

## 小红书（Xiaohongshu）

**入口命令**：`sau xiaohongshu`

### 动作与命令

| 动作 | 命令 |
|------|------|
| 登录 | `sau xiaohongshu login --account <name>` |
| 校验 cookie | `sau xiaohongshu check --account <name>` |
| 上传视频 | `sau xiaohongshu upload-video ...` |
| 上传图文 | `sau xiaohongshu upload-note ...` |

### 必填 / 可选参数

- **upload-video** 必填：`--account` `--file` `--title`
  可选：`--desc` `--tags`（逗号分隔） `--schedule` `--thumbnail` `--debug` `--headless` / `--headed`
- **upload-note** 必填：`--account` `--images`（多张） `--title`
  可选：`--note` `--tags` `--schedule` `--debug` `--headless` / `--headed`

### 约束

1. `upload-video` 每次命令**仅一个视频文件**。
2. `upload-note` 每次命令支持**多张图片**；图文正文用 `--note`。
3. `--tags` 使用逗号分隔；`--schedule` 格式 `YYYY-MM-DD HH:MM`，不传立即发布。
4. **登录二维码**：若登录流程生成本地二维码图片，优先直接把图片展示 / 发送给用户扫码，不要只回传路径。
5. **合规提醒**：小红书对标题党、营销话术、外部导流较敏感，文案避免使用违规词与明显广告用语。
6. **运行模式**：用户明确要求无头 / 有头时才传 `--headless` / `--headed`。

---

## Bilibili（哔哩哔哩）

**入口命令**：`sau bilibili`（运行时会**自动准备 `biliup`**，无需手动安装）

### 动作与命令

| 动作 | 命令 |
|------|------|
| 登录 | `sau bilibili login --account <name>` |
| 校验账号 | `sau bilibili check --account <name>` |
| 上传视频 | `sau bilibili upload-video ...` |

### 必填 / 可选参数

- **upload-video** 必填：`--account` `--file` `--title` `--desc` `--tid`（分区码）
  可选：`--tags`（逗号分隔） `--schedule "YYYY-MM-DD HH:MM"`

### 约束

1. **`--tid` 强制**：第一版必须传分区码（如科技数码类分区码），不传会失败。分区码取值参考 B 站投稿分区表。
2. **登录必须由用户在本地真实终端执行**：登录是交互式 TUI / 二维码流程，Agent 不应在非交互 / 沙箱环境硬跑 `sau bilibili login`；若终端二维码显示不完整，提醒用户直接打开当前目录下的 `qrcode.png` 扫码。
3. **无图文能力**：Bilibili 链路仅支持视频上传。
4. **标题长度**：B 站标题上限约 80 字，超出会被截断（`post-bilibili` 脚本已做截断保护）。
5. **频控**：新号连续投稿可能触发 `code 601 上传过快`；遇此错误 sleep 几分钟后重试即可，非脚本故障。
6. **`biliup` 自动管理**：首次运行相关命令时程序自动下载 / 更新 `biliup`，不要要求用户手动安装。
7. **定时格式**：`--schedule` 走 `sau` 统一时间格式 `YYYY-MM-DD HH:MM`。

---

## 视频号（Channels / 微信视频号）⚠️ 实验性

**当前状态**：`social-auto-upload` 中视频号**没有 `sau` CLI、也没有独立 skill**。仅有骨架式上传器 `uploader/tencent_uploader` 与调试入口 `examples/upload_video_to_tencent.py`，**核心页面交互逻辑仍是空壳**，需要手动补全后才能真实发布。

### 可用接口（来自 `uploader.tencent_uploader.main`）

```python
from uploader.tencent_uploader.main import (
    TencentVideo, TencentNote,
    TENCENT_PUBLISH_STRATEGY_IMMEDIATE,
    TENCENT_PUBLISH_STRATEGY_SCHEDULED,
)

# 视频
TencentVideo(
    title="标题",
    file_path="videos/demo.mp4",
    tags=["标签1", "标签2"],
    publish_strategy=TENCENT_PUBLISH_STRATEGY_IMMEDIATE,  # 或 _SCHEDULED
    publish_date=0,            # 定时发布时传 datetime
    account_file="cookies/tencent_uploader/account.json",
    desc="视频简介",
    thumbnail_path=None,       # 可选封面
    short_title="短标题",
    category=None,
    is_draft=False,
).tencent_upload_video()

# 图文
TencentNote(
    image_paths=["videos/demo.png", "videos/demo1.png"],
    note="图文正文 #话题",
    tags=["标签1", "标签2"],
    publish_strategy=TENCENT_PUBLISH_STRATEGY_IMMEDIATE,
    publish_date=0,
    account_file="cookies/tencent_uploader/account.json",
    title="图文标题",
    is_draft=False,
).tencent_upload_note()
```

### 约束与风险（必须告知用户）

1. **未完成**：`fill_title_and_tags` / `wait_for_upload_complete` / `set_thumbnail` / `submit_publish`（视频）与 `switch_to_note_mode` / `upload_note_images` / `fill_note_title_and_tags` / `submit_publish`（图文）等方法目前是骨架，需自行补全页面交互逻辑。
2. **不能承诺一键自动发布**：在核心方法补全前，视频号仅能作为本地调试入口，Agent 不应向用户保证自动化成功。
3. **登录态**：需用户自行准备 `cookies/tencent_uploader/account.json` 账号文件。
4. **调试入口**：`examples/upload_video_to_tencent.py` 可直接运行做本地调试，补全上述方法后即可复用。
5. **合规**：视频号属微信生态，自动化发布有较强风控与 ToS 限制，自行评估风险。

> 接入示例见 `scripts/examples/tencent_example.py`（标记 `EXPERIMENTAL`，仅演示接口调用，不保证真实发布成功）。
