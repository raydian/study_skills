# 运行前提（Runtime Requirements）

本技能依赖开源项目 `social-auto-upload` 提供的 `sau` CLI。发布前确保以下前提成立。

## 1. 安装 social-auto-upload

在项目根目录（已克隆的仓库）执行：

```bash
uv pip install -e .
```

安装后应有 `sau` 命令可用（或始终用 `uv run sau ...`）。

## 2. 安装 patchright 浏览器

上传器基于 `patchright`（Playwright 分支）驱动 Chromium：

- Windows (PowerShell)：
  ```powershell
  $env:PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright"; patchright install chromium
  ```
- macOS / Linux (bash / zsh)：
  ```bash
  PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright" patchright install chromium
  ```

## 3. 调用 sau 的几种方式

- 已在 PATH：
  ```bash
  sau douyin --help
  ```
- 虚拟环境未激活（PowerShell）：
  ```powershell
  .\.venv\Scripts\Activate.ps1
  sau douyin --help
  ```
- 直接调用可执行文件（PowerShell）：
  ```powershell
  .\.venv\Scripts\sau.exe douyin --help
  ```
- 用 uv：
  ```bash
  uv run sau douyin --help
  ```

## 4. 账号与配置文件

- 账号通过 `--account <name>` 区分，一个 `account_name` 对应一个账号文件（cookie / 登录态）。
- 仓库根目录 `conf.example.py` 复制为 `conf.py`，按需配置代理等（如 YouTube 场景的 `YT_PROXY`；抖音 / 小红书通常无需）。
- 抖音触发短信二次验证时，CLI 优先读取项目根 `verify_code.txt`。

## 5. 无头 / 有头模式

- `--headless`：无头（后台运行，适合 CLI / 服务端 / agent 场景）。
- `--headed`：有头（弹出浏览器窗口）。
- 仅在用户明确要求时显式传入；未指定则按平台默认。
- 登录生成的本地二维码图片，应直接展示 / 发送给用户扫码，不要只回传路径。

## 6. 环境注意

- 登录是交互式流程，**必须由用户在本地真实终端完成**；Agent 不应在 WorkBuddy 沙箱 / 非交互环境硬跑 `login`。
- B 站上传可能受沙箱网络拦截，必要时请用户在独立终端运行上传命令（参考 `post-bilibili` 技能的处理方式）。
- 视频号链路无 `sau`，需直接调用 `uploader/tencent_uploader`（见 `platform-rules.md`）。
