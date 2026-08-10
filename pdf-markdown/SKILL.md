---
name: pdf-markdown
description: Use when a PDF textbook, curriculum standard, handout, exam, atlas, or reference document must become traceable Markdown with extracted images, cleaned structure, and chapter or unit documents, especially when MinerU, OCR, tables, formulas, or complex layouts are involved.
---

# PDF Markdown

## Core rule

PDF 原文转换必须分成三个有依赖关系的阶段：

```text
PDF
  ↓ MinerU 原始转换
原始稿 + images/ + MinerU 结构化结果 + manifest
  ↓ 只基于原始稿格式化
格式化完整稿
  ↓ 只基于格式化稿拆分
拆分/章节/、拆分/单元/
```

原始稿负责可追溯，格式化稿负责连续阅读，拆分稿负责按结构使用。不得跳过原始稿，不能把格式化或拆分结果写回原始稿，也不能把教材原文转换稿直接放入 `high_school/`。

读取 `references/pdf-markdown-contract.md` 后再执行转换。

## 默认入口

项目根目录执行：

```bash
python scripts/pdf_markdown_pipeline.py run \
  --pdf "原始资料/教材/地理/普通高中教科书·地理必修 第一册.pdf" \
  --subject 地理 --kind textbook
```

分阶段重跑：

```bash
python scripts/pdf_markdown_pipeline.py convert --pdf <PDF> --subject <学科> --kind textbook
python scripts/pdf_markdown_pipeline.py import-mineru --mineru-output <已完成的 MinerU 输出目录> --pdf <PDF> --subject <学科> --kind textbook
python scripts/pdf_markdown_pipeline.py format --raw <输出目录>/<文件名>.md
python scripts/pdf_markdown_pipeline.py split --formatted <输出目录>/<文件名>-格式化.md
python scripts/pdf_markdown_pipeline.py validate --output-dir <输出目录>
```

### 引擎规则

- `convert` 和 `run` 默认使用 MinerU 的 `pipeline` 后端，中文默认语言为 `ch`。
- 可执行文件按以下顺序查找：`--mineru-bin`、`MINERU_BIN`、当前 PATH、项目 `.venv-mineru/bin/mineru`、项目 `.venv/bin/mineru`。
- Apple Silicon 不要求 MPS 可用；MPS 不可用时由 MinerU pipeline 使用 CPU 完成转换。
- MinerU 不可用时必须明确失败并停止，不得悄悄改用其他工具。需要显式回退时使用 `--engine pdfplumber`，并在结果中保留回退引擎信息。
- 如果 MinerU 已经完成但进程收尾失败或任务需要恢复，可用 `import-mineru` 导入包含 `auto/`、Markdown、图片和 `content_list_v2.json` 的已有输出，然后继续 `format`、`split`、`validate`；不能把未完成目录当作成功结果。
- MinerU 的模型下载、OCR、版面、表格和图片处理由 MinerU 原始阶段完成；原始稿不做人工改写。

## 输出目录

教材：

```text
markdown/<学科>/<PDF 文件名>/
  <PDF 文件名>.md                 # MinerU 原始 Markdown
  <PDF 文件名>-格式化.md           # 清理后的完整稿
  conversion-manifest.json
  images/                          # 所有阶段共用，只有一份
  mineru/                          # MinerU 原始 Markdown 和 JSON 结构化结果
  拆分/
    README.md
    章节/
      README.md
      01-第一章 xxx.md
    单元/
      README.md
      01-第一单元 xxx.md
```

非教材资料使用 `markdown/<学科>/原始资料/<PDF 文件名>/`。同一个 PDF 独占一个输出目录；PDF 原文件仍留在 `原始资料/`。

拆分文档不复制图片：

```markdown
![图片说明](../../images/page-001-figure-01.jpg)
```

## Stage 1：MinerU 原始稿和图片

1. 确认 PDF、学科、资料类型和输出目录；记录源文件 SHA-256。
2. 调用 MinerU：`mineru -p <PDF> -o <临时目录> -b pipeline -l ch`。
3. 将 MinerU 生成的 Markdown 原样导入 `<文件名>.md`，图片导入根目录 `images/`，JSON 结构化结果导入 `mineru/`。
4. 生成 `conversion-manifest.json`，记录引擎、命令、模型语言、页数、页面结构块、图片、警告和链接校验结果。
5. 优先保留教材正文图、地图、图表、流程图、实验装置图、题图和无法可靠重建的表格图；不主动复制装饰背景。

MinerU 的原始 Markdown 可能没有页面注释。此时必须保留 `mineru/*_content_list_v2.json` 或同等结构化结果，以页面记录提供追溯；不能为了添加页码而重新改写 MinerU 原文。若使用显式 `pdfplumber` 回退，原始稿应写入 `<!-- 第 N 页 -->` 页面标记。

原始阶段失败时：

- 不生成看似完整的格式化稿或拆分稿；
- 保留错误信息、命令和受影响页面；
- PDF 损坏、模型下载失败、端口/权限失败、输出缺页或图片断链都必须进入 manifest 警告；
- 只有用户或调用者明确指定 `--engine pdfplumber` 时才使用回退引擎。

## Stage 2：格式化完整稿

格式化只读取 `<文件名>.md` 和同目录图片，不重新读取 PDF，也不凭常识补写内容。

允许并应当处理：

- 删除目录中的重复章节标题，但保留正文第一次真实章节标题；
- 删除稳定重复的页眉、页脚、出版社行、孤立页码和 `cid:` 残片；
- 合并 MinerU 产生的跨行标题，例如 `第 四章` + `地貌`；
- 统一 `第 X 章`、`第 X 节`、`第 X 单元`、`Unit N` 和高置信度小节标题层级；
- 合并无意义的页面断行，保留段落、题目、选项、答案、图注、公式、表格、脚注、索引、附录和图片引用；
- 保留 `<!-- 来源页：N -->` 或 MinerU JSON 的页面追溯信息。

不得仅因一行只有数字就删除它；不得把目录、页眉、题号或图号误当成正文标题；模糊内容保留原样并加入人工复核 warning。

## Stage 3：按单元和章节拆分

拆分只读取格式化稿，并只在高置信度结构标题处切分：

- `第 X 章`、`Chapter N` → `拆分/章节/`；
- `第 X 单元`、`Unit N`、`Welcome Unit` → `拆分/单元/`。

普通小标题、题号、图注和目录条目不得触发拆分。每个拆分文件保留教材标题、所属结构标题、转换说明、页面追溯注释和原始相对图片链接。每类目录生成 README，根目录 README 汇总全部拆分文件。没有明确“单元”层级时，不人为创建单元文档。

## Validation gate

执行：

```bash
python scripts/pdf_markdown_pipeline.py validate --output-dir <输出目录>
```

必须同时满足：

- 原始稿、格式化稿、manifest 和拆分 README 存在；
- MinerU `content_list_v2` 页数与 manifest 页面记录一致；
- 原始稿、格式化稿和拆分稿的图片链接全部存在；
- 每张提取图片的引用状态、来源页和去重关系可从 manifest 追溯；
- 章节/单元标题没有因目录或页眉重复生成多个文档；
- 没有明显 `cid:`、重复艺术字、错序栏文本、孤立页脚或断裂题目关系；
- OCR、缺页、模型/命令失败、过滤图片和人工复核项均已记录。

如果质量不能确定，必须列出具体页码或章节，不能只写“转换完成”。

## Boundary

本技能只负责 PDF 原始转换、图片提取、格式化和单元/章节拆分。用户要求生成学习型章节笔记时，再使用 `$chapter-notes`；不得把整份教材转换稿直接当作正式学习笔记。
