#!/usr/bin/env bash
# 抖音 post-media 快速命令模板（占位符请替换为真实值）
set -euo pipefail

ACCOUNT="my_account"                 # 自定义 account_name，对应一个账号文件
VIDEO="videos/demo.mp4"
COVER="videos/demo.png"
TITLE="示例标题"
DESC="示例简介"
TAGS="标签1,标签2"
SCHEDULE="2026-08-04 10:00"          # 不定时发布可去掉 --schedule

# 登录（请在本地真实终端执行，扫码完成）
sau douyin login --account "$ACCOUNT"

# 校验 cookie
sau douyin check --account "$ACCOUNT"

# 上传视频
sau douyin upload-video \
  --account "$ACCOUNT" \
  --file "$VIDEO" \
  --title "$TITLE" \
  --desc "$DESC" \
  --tags "$TAGS" \
  --thumbnail "$COVER" \
  --schedule "$SCHEDULE" \
  --headless

# 上传图文（多张图片，最多 35 张，不支持 GIF）
# sau douyin upload-note \
#   --account "$ACCOUNT" \
#   --images "$VIDEO".png extra1.png extra2.png \
#   --title "$TITLE" \
#   --note "图文正文" \
#   --tags "$TAGS" \
#   --schedule "$SCHEDULE" \
#   --headless
