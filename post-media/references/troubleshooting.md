# 故障排查（Troubleshooting）

## 找不到 `sau` 命令

```powershell
.\.venv\Scripts\Activate.ps1
sau douyin --help
```
```powershell
.\.venv\Scripts\sau.exe douyin --help
```
```bash
uv run sau douyin --help
```
若项目未安装：
```bash
uv pip install -e .
```

## cookie 无效 / 已过期

先检查状态：
```bash
sau <platform> check --account <account>
```
输出 `invalid` 则重新登录：
```bash
sau <platform> login --account <account>
```

## 无头登录二维码处理

- 查找 CLI 打印出的临时二维码图片路径。
- **不要只把路径回给用户**，优先直接把本地图片展示 / 发送给用户扫码。
- 终端二维码显示不正常时，改用保存下来的图片路径，不要反复尝试随机终端设置。

## 上传参数缺失

- 视频上传最少需要：`--account` `--file` `--title`
- 图文上传最少需要：`--account` `--images` `--title`
- `--note` 当前为可选图文正文。

## 图片限制（图文上传）

- `upload-note` **不支持 GIF**。
- 每次最多 **35 张图片**。
- 超出限制先减少图片数量 / 替换格式再重试。

## 定时发布

- 时间格式：`YYYY-MM-DD HH:MM`。
- 不需要定时发布时，去掉 `--schedule` 即为立即发布。

## Bilibili 专属

- 必须传 `--tid`（分区码），否则失败。
- 新号连续投稿触发 `code 601 上传过快`：sleep 几分钟重跑，非脚本故障。
- 登录必须在本地真实终端执行；二维码不完整时打开 `qrcode.png` 扫码。
- 上传受沙箱网络拦截时，请在用户独立终端运行上传命令。

## 视频号专属

- 无 `sau` CLI，错误使用 `sau 视频号 ...` 会报未知命令。
- 当前仅骨架式 `uploader/tencent_uploader`，核心方法未实现，发布会失败或停留——属预期（实验性），见 `platform-rules.md` 的「视频号」。
