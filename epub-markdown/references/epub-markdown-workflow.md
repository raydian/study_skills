# EPUB → Markdown 工作流（详细）

适用于把一本 EPUB 电子书按"文章/章节"拆成多个 Markdown 文件，并把图片提取到 `images/`。
pandoc 必须已安装（`pandoc --version`）。本流程在 乡土中国.epub 上验证通过。

## 1. 侦察 EPUB 结构

```bash
cd /tmp && rm -rf epub_x && mkdir epub_x && cd epub_x
unzip -q "/path/to/book.epub"
# 看目录顺序与标题
cat OEBPS/toc.ncx        # <navLabel><text> 是文章标题，<content src="Text/xxx.html"/> 是对应文件
# 看图片目录
ls OEBPS/Images
```

- 文章通常对应 `OEBPS/Text/chapterNNN.html`（也可能含 front001.html 等前置页）。
- 每个 XHTML 一般只有一个顶层 `<h1>` 作为文章标题。
- 装饰性无文字页（如仅背景图的封面页）可跳过。

## 2. 整体转换（关键步骤）

```bash
OUT="/abs/path/markdown/<学科>/<书名>"
mkdir -p "$OUT"
cd "$OUT"                              # 必须在输出目录运行，保证图片用相对路径
pandoc "/abs/path/book.epub" --extract-media=images -t markdown -o _combined.md
```

要点：
- **必须整本转换**，不要逐 XHTML 文件转换——逐文件时 pandoc 会按错误目录解析 `../Images/...` 而丢失图片。
- `--extract-media=images` 用相对路径（相对 cwd=输出目录），生成的图片引用才是 `images/xxx.jpg`。用绝对路径会得到不可用绝对路径。
- 输出 `_combined.md` 中每篇文章是一个顶层 `# 标题`，按阅读顺序排列；图片引用形如 `images/Images/Cover.jpg`（注意嵌套子目录）。

## 3. 清理 pandoc 产物

对 `_combined.md`（或直接对拆分后的文件）做以下处理：

1. **丢弃第一个 `# ` 之前的内容**（封面 SVG 块、空锚点 `[]{#...}`）。
2. 删除围栏 div 标记：`::: zhengwen`、`:::` 等整行。
3. 删除行内空锚点：`[]{#chapter001.html}` 等 → 用正则 `\[\]\{#[^}]*\}` 删除。
4. 去掉标题上的 pandoc 属性花括号：把 `# 乡土本色 {#chapter002.html_a007}` 变为 `# 乡土本色`（对以 `#` 开头的行，去掉 `{[^{}]*}`）。
5. 删除被转坏的脚注标记（多见于"附录"类章节）：
   - 形如 `[^\[1\]^](#chapter017.html_m1)` 和 `[\[1\]](#chapter017.html_w1)`。
   - **用精确字符串替换（单反斜杠形式）**，不要写 raw-string 正则（raw 会变成双反斜杠而匹配不上）：
     ```python
     fnmark = '[^\\[1\\]^](#chapter017.html_m1)'   # 普通字符串 -> 单反斜杠
     fnback = '[\\[1\\]](#chapter017.html_w1)'
     text = text.replace(fnmark, '').replace(fnback, '')
     ```
6. 合并 3 个及以上连续空行为 2 个。
7. **剔除非文章内容的推广/水印块**（多见于某章末尾或全书末尾）：
   - 特征短语：欢迎关注公众号、后台留言/推送、现已整理的作家与系列作品、回复名称获取图书、AZW3+EPUB+MOBI、二维码/网盘/提取码广告。
   - 做法：用这些**特征短语**做整行删除（Python `any(m in line for m in markers)`），删除后顺手去掉尾部空行。
   - 注意：**不要用** "资源""获取" 这类常见词做匹配——它们是正文高频词（如"向环境获取资源"），误删会破坏文章。只删特征短语命中的行。
   - "版权所有·侵权必究" 若作为书籍版权页内容则保留；仅当它作为独立尾部水印行出现时才删。

## 4. 按文章拆分

- 以 `^# ` 为分隔切分 `_combined.md`（每个顶层标题=一篇文章）。
- 顺序编号 `NN-标题.md`（01 起），标题取自 H1 文本（去掉 `{...}`）。
- 输出目录 `markdown/<学科>/<书名>/` 下。

## 5. 图片扁平化

pandoc 常把图片写到 `images/Images/...`（保留 EPUB 内子目录名）。把它展平：

```bash
cd markdown/<学科>/<书名>
mv images/Images/* images/ 2>/dev/null; rmdir images/Images 2>/dev/null
# 把所有 md 里的 images/Images/ 改成 images/
```

## 6. 可选索引

写 `README.md`，列出全部文章并链接，方便浏览（Quartz 等静态站也适用）。

## 7. 校验

```bash
cd markdown/<学科>/<书名>
# 所有图片引用都能解析
for f in [01]*.md 20-*.md; do
  for img in $(grep -o 'images/[^) ]*' "$f" | sort -u); do
    [ -f "$img" ] || echo "MISS $img in $f"
  done
done
# 不应残留产物
grep -l ':::\|\[\]\{#\|(#chapter\|Images/' [01]*.md 20-*.md || echo "NONE"
```

- 文章文件以 `0` 或 `1` 开头时用 `[01]*.md`；以 `2` 开头的（如 `20-附录.md`）要单独列入 glob，否则会被漏掉。
- 确认每篇文件首行都是干净的 `# 标题`。
