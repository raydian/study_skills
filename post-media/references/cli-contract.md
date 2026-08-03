# CLI 命令契约（抖音 / 小红书 / Bilibili）

本文件给出三条已就绪平台的精确命令签名。视频号无 CLI，见 `platform-rules.md` 的「视频号」。

> 默认假设当前环境已安装并可调用 `sau` 命令（或可用 `uv run sau ...`）。

---

## 通用约定

- 账号：`--account <name>` 为用户自定义的 `account_name`，一个名对应一个账号文件，支持多账号隔离与并发。
- 定时：`--schedule "YYYY-MM-DD HH:MM"`；**不传即立即发布**。
- 标签：`--tags` 使用英文逗号分隔，如 `tag1,tag2`。
- 模式：`--headless` / `--headed` 仅在用户明确要求时显式传入。
- `check` 输出：`valid`（可用） / `invalid`（缺失或失效）。

---

## 抖音 douyin

### 登录
```bash
sau douyin login --account <account>
```
生成 / 刷新 cookie；若生成二维码图片，直接展示给用户扫码。

### 校验
```bash
sau douyin check --account <account>
```

### 上传视频
```bash
sau douyin upload-video \
  --account <account> \
  --file <video-path> \
  --title "<title>" \
  [--desc "<description>"] \
  [--tags tag1,tag2] \
  [--schedule "YYYY-MM-DD HH:MM"] \
  [--thumbnail <image-path>] \
  [--product-link <url>] \
  [--product-title "<title>"] \
  [--debug] [--headless | --headed]
```

### 上传图文
```bash
sau douyin upload-note \
  --account <account> \
  --images <image-1> [image-2 ...] \
  --title "<title>" \
  [--note "<content>"] \
  [--tags tag1,tag2] \
  [--schedule "YYYY-MM-DD HH:MM"] \
  [--debug] [--headless | --headed]
```

---

## 小红书 xiaohongshu

### 登录
```bash
sau xiaohongshu login --account <account>
```

### 校验
```bash
sau xiaohongshu check --account <account>
```

### 上传视频
```bash
sau xiaohongshu upload-video \
  --account <account> \
  --file <video-path> \
  --title "<title>" \
  [--desc "<description>"] \
  [--tags tag1,tag2] \
  [--schedule "YYYY-MM-DD HH:MM"] \
  [--thumbnail <image-path>] \
  [--debug] [--headless | --headed]
```

### 上传图文
```bash
sau xiaohongshu upload-note \
  --account <account> \
  --images <image-1> [image-2 ...] \
  --title "<title>" \
  [--note "<content>"] \
  [--tags tag1,tag2] \
  [--schedule "YYYY-MM-DD HH:MM"] \
  [--debug] [--headless | --headed]
```

---

## Bilibili bilibili

### 登录（需用户在本地真实终端执行）
```bash
sau bilibili login --account <account>
```
程序自动准备 `biliup`；二维码不完整时打开当前目录 `qrcode.png` 扫码。

### 校验
```bash
sau bilibili check --account <account>
```

### 上传视频
```bash
sau bilibili upload-video \
  --account <account> \
  --file <video-path> \
  --title "<title>" \
  --desc "<desc>" \
  --tid <category-id> \
  [--tags tag1,tag2] \
  [--schedule "YYYY-MM-DD HH:MM"]
```
- `--tid` 第一版**必须传**（分区码）。
- 程序自动准备 / 更新 `biliup`。
