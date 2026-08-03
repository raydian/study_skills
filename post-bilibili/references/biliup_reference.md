# biliup-rs 参考

`biliup-rs` 是开源（Rust）的 B 站命令行投稿工具，把 B 站网页端"上传视频"那套协议
（分片传 upos、提交稿件）封装成一条命令。预编译单文件二进制，无需运行时。

仓库：https://github.com/biliup/biliup-rs

## 1. 安装

三种方式任选：

```bash
# 方式 A：下载预编译二进制（推荐，macOS arm64 已验证）
# 到 https://github.com/biliup/biliup-rs/releases 取 biliupR-<版本>-aarch64-macos.tar.xz
# 解压后把 biliup 放到 ~/bin 并 chmod +x，移除隔离标记：
xattr -d com.apple.quarantine ~/bin/biliup

# 方式 B：cargo
cargo install biliup

# 方式 C：homebrew
brew install biliup
```

> 本技能脚本 `scripts/publish.py` 在找不到 biliup 时会自动尝试方式 A 下载安装。

## 2. 登录（必须人工，且不能在 WorkBuddy 沙箱内完成）

B 站投稿需**已实名/绑定手机**的账号，首次登录要手机 App 扫码确认。扫码是交互式 TUI 菜单，
无法由 Agent 驱动，必须在用户本机的**独立终端**（macOS 终端.app / iTerm）里执行：

```bash
~/bin/biliup -u ~/.bilibili/cookies.json login
```

菜单按 ↓ 选「扫码登录」回车 → 终端出现二维码 → 手机 B 站 App 扫一扫并点「确认登录」。
成功后登录态写入 `~/.bilibili/cookies.json`，之后投稿免登录。

## 3. 上传命令（publish.py 内部调用形式）

```bash
biliup -u ~/.bilibili/cookies.json upload <视频.mp4> \
  --title "标题（≤80字）" \
  --tid 201 \
  --copyright 1 \
  --tag "标签1,标签2,标签3" \
  --desc "视频简介..." \
  --cover "封面.png"
```

常用参数：

| 参数 | 含义 | 说明 |
|---|---|---|
| `--title` | 稿件标题 | **≤80 字**，超出会被 B 站截断 |
| `--tid` | 分区 ID | 见下方分区码表 |
| `--copyright` | 版权 | `1`=自制，`2`=转载 |
| `--tag` | 标签 | 逗号分隔，建议 3–8 个 |
| `--desc` | 简介 | 支持换行，纯文本 |
| `--cover` | 封面 | 本地图片路径（PNG/JPG） |
| `--dtime` | 延时发布 | Unix 时间戳（秒），用于定时发布 |
| `--source` | 来源 | 投稿来源说明 |

## 4. 分区 tid 常用码表

| tid | 分区 |
|---|---|
| 17 | 单机游戏 |
| 65 | 综艺 |
| 86 | 纪录片 |
| 121 | 野生技术（趣味软件） |
| 138 | 科技（互联网） |
| 171 | 电子竞技 |
| 188 | 娱乐 |
| 201 | **科学科普**（知识类课程首选） |
| 205 | 实时象棋 |
| 211 | 动画 |
| 228 | 护肤美妆 |
| 230 | 生活 |
| 231 | 美食 |
| 232 | 动物圈 |
| 233 | 鬼畜 |
| 234 | 时尚 |
| 235 | 影视 |
| 244 | 知识（学习区，亦可选） |

> 高中/学科课程类建议 `tid=201`（科学科普）或 `tid=244`（知识）。

## 5. 已知问题与规避

### 5.1 `Error: error decoding response body / EOF while parsing a value at line 1 column 0`
**现象**：login 或 upload 时拉取接口拿到空响应，JSON 解析失败。
**根因**：本机/沙箱代理（`HTTP_PROXY`/`HTTPS_PROXY`）把 B 站流量送错上游，返回空响应。
**解决**：让 biliup 直连 B 站——运行前 `unset` 所有代理变量（publish.py 已固化此行为）。

### 5.2 WorkBuddy 沙箱拦截 B 站（关键坑）
**现象**：在 WorkBuddy 内无论带不带代理变量都连不上 B 站，报 EOF / connection reset；
但用户浏览器能正常访问 B 站。
**根因**：WorkBuddy 的 agent 沙箱网络代理（`sandbox-c`，监听 `127.0.0.1:65261`）放行百度等
站点但**拦截 B 站**，且透明劫持所有出网流量，所以 `env -u` 清掉代理变量也救不回来。
**解决**：
- **登录**必须在 WorkBuddy 之外的独立终端完成（见第 2 节）。
- **上传**：先尝试在 WorkBuddy 内跑 `publish.py --go`；若仍 EOF / connection reset，
  改请用户在独立终端运行同一命令。

### 5.3 `code 601 上传过快请稍后`
**现象**：新号/小号连续投稿被临时频控。
**解决**：这不是脚本问题，是账号侧限制。等几分钟重跑 `publish.py --go` 即可。
publish.py 已内置条间 `sleep 3` 降低触发概率。

### 5.4 客户端接口失效，回退 APP 接口
**现象**：日志出现"客户端接口已失效，将使用 APP 接口"后"APP 接口投稿成功"。
**说明**：正常回退，无需处理。

## 6. 验证二进制可用

```bash
biliup --version
biliup upload --help
```
