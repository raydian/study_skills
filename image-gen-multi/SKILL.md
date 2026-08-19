---
name: image-gen-multi
description: Generate or edit images through three pluggable channels — foxcode (OpenAI-compatible reseller), Qwen Bailian (bailian-cli bl), and Volcengine Ark (ark-cli) — through one unified entry script with auto channel selection and fallback. Use when the user asks to 生成图片, 画一张, 文生图, 图生图, 图片编辑, 风格迁移, 换背景, or generate images/variations/edits without naming a specific channel; the channel order for auto mode is foxcode → volcengine(arkcli) → bailian(bl).
---

# Image Gen Multi（多渠道生图）

统一入口生成/编辑图片，支持三个可插拔渠道，同一套参数自动路由与降级。

## 渠道与优先级

auto 模式按固定顺序选择可用渠道（已定稿）：

1. **foxcode**（OpenAI 兼容三方）—— 需 `FOX_CODE_API_KEY`
2. **volcengine**（火山引擎 arkcli）—— 需 `arkcli` 已 SSO 登录
3. **bailian**（千问百炼 bl）—— 需 `bl` CLI 可用

用户显式指定渠道（`--provider foxcode|volcengine|bailian`）优先于 auto。
主渠道失败时按上述顺序自动降级重试（`--fallback`，默认开启）。

## 快速开始

```bash
# 渠道状态探测
python3 scripts/check_providers.py

# 文生图（auto 自动选渠道）
python3 scripts/generate_image.py --prompt "一只柴犬在樱花树下，日系摄影风格" --size 16:9

# 指定渠道
python3 scripts/generate_image.py --provider foxcode --prompt "赛博朋克城市" --quality high
python3 scripts/generate_image.py --provider bailian --prompt "山水画" --watermark false
python3 scripts/generate_image.py --provider volcengine --prompt "未来城市海报"

# 图生图 / 编辑
python3 scripts/generate_image.py --prompt "把背景改成星空" --input-image ./input.png

# 产物校验
python3 scripts/verify_image.py ./output/
```

## 工作流

1. **解析请求**：判断文生图 / 图生图 / 批量（`--n`），提取 prompt、尺寸、风格、渠道（若有）。
2. **探测渠道**：`check_providers.py` 或直接运行 `generate_image.py --dry-run` 查看三渠道可用性。
3. **组装参数**：按 Prompt 规范（`references/prompt-guide.md`）组织描述；尺寸归一化为统一格式。
4. **调用统一入口**：`generate_image.py` 完成渠道路由、调用、落盘、manifest 生成。
5. **校验产物**：`verify_image.py` 检查非空、格式、尺寸；失败按优先级降级重试。
6. **交付**：向用户报告生成文件路径与渠道信息。

## 统一参数

| 参数 | 说明 | 示例 |
|---|---|---|
| `--provider` | auto / foxcode / volcengine / bailian | `--provider foxcode` |
| `--prompt` | 图像描述或编辑指令（必填） | `--prompt "赛博朋克城市"` |
| `--model` | 渠道模型 ID（默认按渠道） | `--model gpt-image-2` |
| `--size` | 尺寸：比例（16:9）或像素（1024x1024） | `--size 1536x1024` |
| `--quality` | 质量档位（foxcode：low/medium/high/auto） | `--quality high` |
| `--n` | 生成张数（默认 1） | `--n 2` |
| `--seed` | 随机种子（渠道支持时） | `--seed 42` |
| `--negative-prompt` | 负面提示（渠道支持时） | `--negative-prompt "模糊, 变形"` |
| `--watermark` | 是否加水印（bailian：true/false） | `--watermark false` |
| `--input-image` | 参考图路径（提供则为图生图） | `--input-image ./img.png` |
| `--out-dir` | 产物目录（默认 ./output） | `--out-dir ./output` |
| `--out-prefix` | 文件名前缀（默认 image） | `--out-prefix cover` |
| `--fallback` / `--no-fallback` | 渠道降级开关（默认开） | `--no-fallback` |
| `--json` | 输出机器可读结果 | `--json` |
| `--dry-run` | 只探测渠道不生图 | `--dry-run` |

## 环境变量

```bash
# foxcode（必须）
export FOX_CODE_API_KEY="sk-xxxx"                          # Bearer token
export FOX_CODE_BASE_URL="https://dm-fox.rjj.cc/codex/v1"  # 默认值，可覆盖
export FOX_CODE_DEFAULT_MODEL="gpt-image-2"                # 默认模型

# volcengine
#   方式 A（推荐，已验证）：ARK_API_KEY 直调 arkruntime
export ARK_API_KEY="your-ark-api-key"
#   ARK_API_BASE_URL=https://ark.cn-beijing.volces.com/api/v3   # 默认值
export ARK_DEFAULT_MODEL="doubao-seedream-4-5-251128"          # 默认模型
#   方式 B：arkcli +gen（需登录且账号有 agent-plan 或已部署 endpoint）
#   arkcli auth login volc-sso

# bailian
#   bl 登录：bl auth（API Key 或控制台登录），与 bailian-cli 技能共享
```

密钥只放环境变量，技能内不硬编码；模板见 `assets/config.example.env`。

## 各渠道要点

- **foxcode**：OpenAI 兼容 `POST {BASE_URL}/images/generations`；模型 `gpt-image-2`（已验证）；`gpt-image-1` 该渠道 404 不可用；返回 url/b64_json；生成约 60s，超时请给足。
- **volcengine**：优先 `ARK_API_KEY` 直调 arkruntime（OpenAI 兼容，已验证 Seedream 4.5）；未设 Key 时回退 `arkcli +gen`（需 agent-plan profile 或已部署 endpoint）。Seedream 4.5 要求尺寸 ≥ 约 2K，脚本自动换算。
- **bailian**：`bl image generate`（文生图）/ `bl image edit`（图生图）；`--out-dir` 自动下载；支持 `--watermark false`。

详见 `references/providers.md`。

## 产物规范

- 图片落盘：`{out-dir}/{out-prefix}_{idx}_{timestamp}.{ext}`
- 生成 `manifest.json`：provider / model / prompt / created_at / files
- `--json` 输出单行 JSON：`{"provider": "...", "manifest": "..."}`

## 约束

- 不改动渠道方 API 与 CLI 本身；参数不支持的渠道采用「忽略 + stderr 告警」。
- 批量生成前提示成本；内容合规遵循平台规则。
- `bl` 保持本机 1.14.1 不升级（用户约定）。
