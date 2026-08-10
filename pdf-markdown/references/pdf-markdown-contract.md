# PDF to Markdown Conversion Contract

## 1. Stages and dependency

每次完整处理必须按以下顺序执行：

```text
convert: PDF → MinerU 原始 Markdown + images/ + MinerU JSON + manifest
format:  原始 Markdown → 格式化完整 Markdown
split:   格式化 Markdown → 章节/单元独立文档 + README
validate: 检查三阶段产物、页面记录、图片引用和拆分覆盖
```

`format` 不得绕过原始稿重新读取 PDF；`split` 不得直接读取 PDF 或原始稿。三个阶段可以单独重跑，但输入必须来自上一个阶段的已生成产物。

如果 MinerU 已经生成完整 `auto/` 目录，可用 `import-mineru` 将其导入项目目录后继续后两个阶段；导入前必须确认 Markdown、图片和 `content_list_v2.json` 均存在。

## 2. Output contract

教材：

```text
markdown/<学科>/<PDF 文件名>/
  <PDF 文件名>.md
  <PDF 文件名>-格式化.md
  conversion-manifest.json
  images/
  mineru/
    <MinerU 原始 Markdown>
    *_content_list_v2.json
    *_content_list.json
    *_middle.json
    *_model.json
  拆分/
    README.md
    章节/README.md
    章节/01-章节名.md
    单元/README.md
    单元/01-单元名.md
```

非教材资料：

```text
markdown/<学科>/原始资料/<PDF 文件名>/
```

规则：

- `<PDF 文件名>` 使用 PDF stem，不包含 `.pdf`；
- 不把转换结果放入 `high_school/`；
- 不把不同 PDF 混在同一目录；
- `<PDF 文件名>.md` 是 MinerU 原始稿，格式化稿和拆分稿不得覆盖它；
- 图片只有根目录 `images/` 一份，拆分文档按自身目录计算相对路径；
- 章节或单元目录只有在源文档存在对应结构时生成；
- 任何失败、缺页、过滤、去重或待复核状态都写入 manifest。

## 3. MinerU contract

默认命令等价于：

```bash
mineru -p <PDF> -o <临时输出目录> -b pipeline -l ch
```

脚本必须支持：

```bash
--engine mineru|pdfplumber       # 默认 mineru
--mineru-bin <path>
--mineru-backend pipeline
--mineru-language ch
```

恢复已有 MinerU 输出：

```bash
python scripts/pdf_markdown_pipeline.py import-mineru \
  --mineru-output <MinerU 输出目录> --pdf <PDF> --subject <学科> --kind textbook
```

MinerU 原始结果通常位于 `<临时输出>/<stem>/auto/`。导入时：

- Markdown 原文写入输出根目录；
- `auto/images/` 图片写入输出根目录 `images/`；
- `*_content_list_v2.json` 等结构化结果写入 `mineru/`；
- 原始 Markdown 的图片引用必须仍然指向可存在的相对路径；
- 不为了添加页面注释而改写 MinerU 原始正文。

如果 MinerU 未安装、模型下载失败、API 端口无法启动或输出不完整，默认流程必须失败并给出原因。`pdfplumber` 只有在显式指定 `--engine pdfplumber` 时作为回退，不得静默切换。

## 4. Manifest contract

manifest 至少包含：

```json
{
  "schema_version": 2,
  "engine": "mineru",
  "backend": "pipeline",
  "command": ["mineru", "-p", "...", "-o", "...", "-b", "pipeline", "-l", "ch"],
  "source_pdf": "/absolute/path/book.pdf",
  "source_sha256": "...",
  "subject": "地理",
  "source_kind": "textbook",
  "page_count": 134,
  "stages": {
    "raw": "书名.md",
    "formatted": "书名-格式化.md",
    "split": ["拆分/章节/01-第一章.md"]
  },
  "mineru": {
    "language": "ch",
    "source_markdown": "mineru/书名.md",
    "artifacts": ["mineru/书名_content_list_v2.json"]
  },
  "pages": [],
  "images": [],
  "warnings": []
}
```

页面记录至少包含页码、文本字符数、图片路径、OCR 状态和 warning。MinerU 页面信息来自 `content_list_v2.json`；若该文件缺失，`page_count` 可以为空，但必须记录人工复核 warning。图片记录至少包含路径、来源页、尺寸、SHA-256、引用状态、去重关系或过滤原因。

## 5. Raw Markdown contract

MinerU 原始稿必须：

- 保留 MinerU 输出顺序和原始 Markdown 内容；
- 保留正文、标题、公式、图注、表格、题目、选项、答案、脚注、索引、附录和注释；
- 保留有效图片链接或明确占位；
- 与 `mineru/` 中原始 Markdown 和结构化 JSON 可互相追溯；
- 不在原始阶段清理目录、页眉、页脚或人工改写正文。

显式 `pdfplumber` 回退稿应增加 `<!-- 第 N 页 -->` 页面标记，并在 OCR 或内容缺失处写出页面级说明。

## 6. Formatted Markdown contract

格式化稿只能从原始 Markdown 生成，允许：

- 删除稳定重复的目录项、页眉、页脚、出版社信息、`cid:` 残片和重复艺术字；
- 合并明确的跨行章、节、单元和小节标题；
- 将高置信度标题统一为 Markdown 层级；
- 保留页面追溯注释、公式、表格、图片、题目、答案、索引、附录和占位。

不允许：

- 根据摘要、常识或外部资料补写原文；
- 只因数字独立成行就删除；
- 把目录或页眉中的章节名当作正文结构再次输出；
- 用字符数变短证明内容完整。

推荐结构：

```markdown
# 教材名

## 第一章 章名

### 第一节 节名

#### 栏目名
```

## 7. Split contract

只在格式化稿的高置信度结构标题处拆分：

- `第 X 章`、`Chapter N` → `拆分/章节/`；
- `第 X 单元`、`Unit N`、`Welcome Unit` → `拆分/单元/`。

每个拆分文件必须：

- 保留教材标题、所属结构标题、转换说明和页面追溯信息；
- 使用从当前文档目录到根 `images/` 的有效相对路径；
- 在对应 README 中被索引；
- 由格式化稿的连续区间生成，不重新改写知识内容；
- 不复制图片文件。

普通正文小标题、题号、图注和目录条目不得触发拆分。同一类别下同一结构标题只能生成一个文档。

## 8. Validation gate

执行：

```bash
python scripts/pdf_markdown_pipeline.py validate --output-dir <输出目录>
```

至少检查：

1. 原始稿、格式化稿、manifest 和拆分文档存在；
2. `page_count == len(pages)`，或 manifest 明确说明页面结构文件缺失；
3. 原始稿、格式化稿和拆分稿的所有本地链接均可解析；
4. `manifest.images` 中的文件路径、引用状态和去重关系一致；
5. 拆分结构标题没有因目录、页眉或重复标题生成多个文档；
6. 没有明显 `cid:`、重复艺术字、错序栏文本、孤立页脚或题目关系断裂；
7. OCR 页、空页、缺失页、模型失败、过滤图片和人工复核项均有记录。

任何不确定性必须列出具体页面或章节，不得用“完整转换”掩盖未验证内容。
