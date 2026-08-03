#!/usr/bin/env bash
# Bilibili post-media 快速命令模板（占位符请替换为真实值）
set -euo pipefail

ACCOUNT="my_account"                 # 自定义 account_name
VIDEO="videos/demo.mp4"
TITLE="示例标题"
DESC="示例简介"
TID="249"                            # 分区码，必填（第一版强制）
TAGS="标签1,标签2"
SCHEDULE="2026-08-04 10:00"          # 不定时发布可去掉 --schedule

# 登录（必须在本地真实终端执行，扫码完成；二维码不完整时打开 qrcode.png）
sau bilibili login --account "$ACCOUNT"

# 校验账号
sau bilibili check --account "$ACCOUNT"

# 上传视频（程序自动准备 / 更新 biliup，无需手动安装）
sau bilibili upload-video \
  --account "$ACCOUNT" \
  --file "$VIDEO" \
  --title "$TITLE" \
  --desc "$DESC" \
  --tid "$TID" \
  --tags "$TAGS" \
  --schedule "$SCHEDULE"
