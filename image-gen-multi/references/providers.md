# image-gen-multi 渠道参考（providers.md）

三个渠道的详细配置、模型清单与命令速查。SKILL.md 只做路由，细节在此按需加载。

---

## 1. foxcode（OpenAI 兼容三方中转）

### 1.1 基本信息

| 项 | 值 |
|---|---|
| 性质 | OpenAI 兼容三方中转（GPT-Image / Gemini Flash Image 等） |
| Base URL | `https://dm-fox.rjj.cc/codex/v1`（环境变量 `FOX_CODE_BASE_URL` 可覆盖） |
| 鉴权 | `Authorization: Bearer $FOX_CODE_API_KEY` |
| 默认模型 | `gpt-image-2`（环境变量 `FOX_CODE_DEFAULT_MODEL` 可覆盖） |
| 端点 | `POST {BASE_URL}/images/generations`（文生图/图生图） |

### 1.2 已验证事实（2026-08-16 实测）

- **`gpt-image-2` 可用**：`{"model":"gpt-image-2","prompt":"a red apple","size":"1024x1024","n":1}` → HTTP 200，返回 `data[0].url`（临时文件 URL，约 60s 生成）。
- **`gpt-image-1` 不可用**：同请求 → HTTP 404 `请求的资源未找到`。
- 响应结构：`{"created":..., "data":[{"revised_prompt":..., "url":...}], "usage":{...}}`。
- 产物 URL 域：`https://tmp-files.hangbao.cc/generated-images/...`（可直接下载）。
- 模型列表端点：`GET {BASE_URL}/models`（当前 21 个模型，图像相关仅 gpt-image-1/2）。

### 1.3 请求参数（OpenAI 兼容）

| 参数 | 值 | 说明 |
|---|---|---|
| `model` | `gpt-image-2` | 默认 |
| `prompt` | str | 描述/编辑指令 |
| `size` | `1024x1024` / `1536x1024` 等 | 像素尺寸 |
| `quality` | `low` / `medium` / `high` / `auto` | 质量档位 |
| `n` | int | 张数 |
| `image` | base64 data URL | 图生图参考图（OpenAI 兼容） |

### 1.4 示例

```bash
export FOX_CODE_API_KEY=sk-xxx
curl --location --request POST 'https://dm-fox.rjj.cc/codex/v1/images/generations' \
  --header "Authorization: Bearer $FOX_CODE_API_KEY" \
  --header 'Content-Type: application/json' \
  --data-raw '{"model":"gpt-image-2","prompt":"一个小男孩","size":"1536x1024","quality":"high","n":1}'
```

### 1.5 注意

- 三方中转，Base URL 与模型可用性以 FoxCode 控制台为准。
- 生成耗时约 60s，脚本/调用方超时需给足（generate_image.py 默认 300s）。
- 走系统代理（HTTP_PROXY/HTTPS_PROXY）时请求可能偶发超时，可重试。

---

## 2. 火山引擎（Ark）

### 2.1 基本信息

| 项 | 值 |
|---|---|
| 性质 | 火山方舟 MaaS 平台（Seedream 生图 / Seedance 生视频） |
| 方式 A | `ARK_API_KEY` 直调 arkruntime（OpenAI 兼容，**已验证可用**） |
| 方式 B | `arkcli +gen`（官方 CLI，需 agent-plan profile 或已部署 endpoint） |
| 登录 | `arkcli auth login volc-sso`（无浏览器：`--no-browser` / `--no-browser --code`） |
| 默认模型 | `doubao-seedream-4-5-251128`（环境变量 `ARK_DEFAULT_MODEL` 可覆盖） |

### 2.2 方式 A：ARK_API_KEY 直调（推荐）

```bash
export ARK_API_KEY="your-ark-api-key"
curl --request POST "https://ark.cn-beijing.volces.com/api/v3/images/generations" \
  --header "Authorization: Bearer $ARK_API_KEY" \
  --header 'Content-Type: application/json' \
  --data-raw '{"model":"doubao-seedream-4-5-251128","prompt":"一只柴犬在樱花树下","size":"2048x2048","n":1}'
```

**已验证事实（2026-08-16）**：
- `doubao-seedream-4-5-251128` 可用，HTTP 200，约 11.6s 出图，返回 `data[0].url`（TOS 临时 URL）。
- **尺寸要求**：`size` 至少 3686400 像素（约 1920x1920）；`1024x1024` 会报 `InvalidParameter`。脚本 `_size_to_ark` 自动换算（1:1→2048x2048，16:9→2560x1440 等）。
- 响应结构：`{"model":..., "created":..., "data":[{"url":...}]}`。

**鉴权兜底**：未设置 `ARK_API_KEY` 时，脚本自动从 `~/.arkcli/config.yaml` 读取 platform profile 的 `api_key`（本机已配置）。

### 2.3 方式 B：arkcli +gen（官方 CLI）

| Flag | 说明 |
|---|---|
| `--model` | 模型名或 endpoint ID |
| `--n` / `--image-count` | 图片张数（>1 开启连续生成） |
| `--ratio` | 比例：`16:9` / `9:16` / `1:1` |
| `--resolution` | 分辨率 |
| `--seed` | 种子 |
| `--input` | 参考图（本地 `@path`，可重复） |
| `--save-to` | 本地保存目录（默认当前目录；`--save-to=""` 禁用） |
| `--output-format` | `jpeg` / `png` |
| `--no-open` | 不自动打开产物 |
| `--optimize-prompt` / `--prompt-mode` | 服务端 prompt 优化 |
| `--guidance-scale` | CFG 引导强度（float） |
| `--dry-run` | 预览执行计划，不发起请求 |

> **注意**：`arkcli +gen` 用模型名需要 **agent-plan profile**（账号需购买 Agent Plan，`plans get` 可见）；用 **platform profile** 则需要 **endpoint ID（ep-...）**，不能用模型名。本机当前无 Plan 订阅，因此走方式 A 直调。

### 2.4 模型（Seedream 系列）

| 模型 ID | 特点 |
|---|---|
| `doubao-seedream-3-0-t2i-250115` | 轻量快速 |
| `doubao-seedream-4-0-t2i-250115` | 标准质量 |
| `doubao-seedream-4-5-251128` | 高质量（默认建议） |
| `doubao-seedream-5-0-260128` | 最新（2K/3K，支持流式/联网） |

> 模型清单可用 `arkcli models search seedream` 或 `arkcli +gen --dry-run` 确认。
> 若 `--model` 是 endpoint ID，需显式 `--modality image`。

### 2.5 示例

```bash
# 方式 A：ARK_API_KEY 直调（推荐）
python3 scripts/generate_image.py --provider volcengine --prompt "未来城市海报" --size 16:9

# 方式 B：arkcli（需 agent-plan profile 或 endpoint）
arkcli +gen "一只柴犬在樱花树下，日系摄影风格" --model doubao-seedream-4-5-251128 --ratio 1:1 --save-to ./output --no-open
arkcli +gen "把背景改成星空" --input @./input.png --save-to ./output --no-open
```

### 2.6 注意

- 视频任务返回 task id（`--wait` 阻塞等待）；图片任务默认等待并下载。
- 产物保存目录由 `--save-to` 控制，脚本统一传入 `--out-dir`。
- 未登录时 `arkcli auth status` 非 sso，`check_providers.py` 判定为不可用。

---

## 3. 千问百炼（bailian-cli `bl`）

### 3.1 基本信息

| 项 | 值 |
|---|---|
| 性质 | 阿里云百炼官方 CLI |
| 版本 | 本机 `bl` 1.14.1（**约定不升级**） |
| 鉴权 | `bl auth`（API Key 或控制台登录），与 bailian-cli 技能共享 |
| 文生图 | `bl image generate` |
| 图生图 | `bl image edit` |

### 3.2 `bl image generate` flags

| Flag | 说明 |
|---|---|
| `--prompt` | 描述（必填） |
| `--model` | 模型 ID（默认 `qwen-image-3.0`） |
| `--size` | 比例（`3:4` / `16:9` / `1:1`）或像素（`2048*2048`） |
| `--n` | 张数（默认 1，最大 6） |
| `--seed` | 种子 |
| `--negative-prompt` | 负面提示 |
| `--watermark` | true/false |
| `--prompt-extend` | true/false（qwen-image 同步默认 true） |
| `--async` | 返回 task id 不等待 |
| `--concurrent` | 并行请求数 |
| `--out-dir` / `--out-prefix` | 产物目录 / 前缀 |
| `--api-key` / `--base-url` | 覆盖鉴权 |

### 3.3 `bl image edit` flags

| Flag | 说明 |
|---|---|
| `--image` | 源图 URL 或本地路径（可重复，多图融合） |
| `--prompt` | 编辑指令（必填） |
| `--model` | 模型 ID（默认 `qwen-image-3.0`） |
| `--size` | 输出尺寸：比例（`3:4` / `16:9`）或像素（`2048*2048`） |
| `--n` | 张数（默认 1，最大 6） |
| `--seed` | 种子 |
| `--negative-prompt` | 负面提示 |
| `--watermark` | true/false |
| `--out-dir` / `--out-prefix` | 产物目录 / 前缀（默认 edited） |
| `--function` | wanx*-imageedit 功能（默认 description_edit） |

### 3.4 可用模型速查

| 模型 ID | 特点 |
|---|---|
| `qwen-image-3.0` | 默认，通用高质量 |
| `qwen-image-2.0-pro` | 专业质量 |
| `wan2.6-t2i` | 通义万相，异步 |
| `z-image-turbo` | 快速轻量 |
| `wanx2.0-t2i-turbo` | 快速 |

### 3.5 示例

```bash
bl image generate --prompt "一只柴犬在樱花树下" --model qwen-image-3.0 --size 16:9 --n 1 --watermark false --out-dir ./output
bl image edit --image ./input.png --prompt "把背景改成星空" --size 1:1 --out-dir ./output
bl image generate --prompt "产品图" --n 2 --concurrent 3   # 6 张并行
```

### 3.6 注意

- 领域命令细节归 `bailian-gen` 技能（未安装时可 `bl image --help` / `bl image generate --help`）。
- 走 `bl auth` 控制台登录时涉及协议类命令，遵循 `bailian-protocol` 的授权约定。
