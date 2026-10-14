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

项目根目录执行（脚本位于本技能目录 `scripts/pdf_markdown_pipeline.py`）：

```bash
python study_skills/pdf-markdown/scripts/pdf_markdown_pipeline.py run \
  --pdf "原始资料/参考资料/高中必刷题数学必修第一册狂K重点 132.pdf" \
  --out-root "markdown/参考资料"
```

分阶段重跑：

```bash
python study_skills/pdf-markdown/scripts/pdf_markdown_pipeline.py convert --pdf <PDF> --out-root <输出父目录>
python study_skills/pdf-markdown/scripts/pdf_markdown_pipeline.py import-mineru --bundle <MinerU 产出的 zip 或解压目录> --pdf <PDF> --out-root <输出父目录>
python study_skills/pdf-markdown/scripts/pdf_markdown_pipeline.py format  --dir <输出目录>
python study_skills/pdf-markdown/scripts/pdf_markdown_pipeline.py split   --dir <输出目录>
python study_skills/pdf-markdown/scripts/pdf_markdown_pipeline.py validate --dir <输出目录>
```

输出目录 = `<out-root>/<PDF stem>/`。`out-root` 由用户指定（如 `markdown/参考资料`、`markdown/地理`、`markdown/地理/原始资料`），缺省为 `markdown`。

### 引擎规则（MinerU 4.x）

- MinerU 4.x **不再支持** `mineru -p ... -o ... -b pipeline -l ch`。经典「Markdown + images/ + 结构化 JSON」三者齐备的产物由 `mineru-kit parse --format zip` 生成，zip 内是 `markdown.md`、`images/`、`structured_content.json`、`middle_json.json`、`model_output.json`。
- 转换前必须确认模型就绪（4.x 的 `mineru parse` 走 doclib 服务，`mineru-kit parse` 走进程内推理，两者都要求档位资源就绪）：
  ```bash
  ~/mineru_env/bin/mineru-kit models show
  ~/mineru_env/bin/mineru-kit models download --tier standard --source modelscope
  ~/mineru_env/bin/mineru config set parse_server.local.mode managed
  ~/mineru_env/bin/mineru server restart
  ```
  HuggingFace 常不可达，模型源优先 `modelscope`；`basic` 档只需 `MinerU-4_models_torch`，`standard` 档额外需要 `MinerU2.5-Pro-2605-1.2B-GGUF`。
- 可执行文件按以下顺序查找：`--mineru-kit-bin`、`MINERU_KIT_BIN`、`~/mineru_env/bin/mineru-kit`、当前 PATH。
- Apple Silicon 上 VLM 引擎自动解析为 `llama-cpp`，小模型后端为 `torch`；不要求 MPS 可用。纯扫描 PDF（无文本层）必须走 OCR/VLM，`standard` 档实测约 0.3 页/秒。
- MinerU 不可用时必须明确失败并停止，不得悄悄改用其他工具。
- 如果 MinerU 已经完成但任务需要恢复，可用 `import-mineru` 导入已产出的 zip（或解压目录），然后继续 `format`、`split`、`validate`；不能把未完成目录当作成功结果。
- MinerU 的模型下载、OCR、版面、表格和图片处理由 MinerU 原始阶段完成；原始稿不做人工改写。

### 沙箱环境注意（WorkBuddy IDE）

- `Path.mkdir()` / `shutil.rmtree()` 或整目录 `rm` 会触发沙箱代理与批量删除拦截。脚本内的目录创建统一走 `ensure_dir()`（已存在时完全不再调用 `mkdir`），清理只在 `拆分/` 下逐个删除本次不再产出的 `.md`，绝不递归删目录。
- 长任务（132 页纯扫描件 standard 档约 30 分钟）用后台运行，不要在前台等着。

## 输出目录

教材：

```text
markdown/<学科>/<PDF 文件名>/
  <PDF 文件名>.md                 # MinerU 原始 Markdown
  <PDF 文件名>-格式化.md           # 清理后的完整稿
  conversion-manifest.json
  images/                          # 所有阶段共用，只有一份
  mineru/                          # MinerU 原始 Markdown 和 JSON 结构化结果
    structured_content.json
    middle_json.json
    model_output.json
    <PDF 文件名>.md
  拆分/
    README.md
    章节/
      README.md
      01-第一章 xxx.md
    单元/
      README.md
      01-第一单元 xxx.md
```

非教材资料默认使用 `markdown/<学科>/原始资料/<PDF 文件名>/`；用户指定其它位置时以 `--out-root` 为准（例如「放到 markdown/参考资料 下」→ `--out-root markdown/参考资料`，输出为 `markdown/参考资料/<PDF 文件名>/`）。同一个 PDF 独占一个输出目录；PDF 原文件仍留在 `原始资料/`。

拆分文档不复制图片：

```markdown
![图片说明](../../images/page-001-figure-01.jpg)
```

## Stage 1：MinerU 原始稿和图片

1. 确认 PDF、学科、资料类型和输出目录；记录源文件 SHA-256。
2. 调用 MinerU：`mineru-kit parse <PDF> --pages all --tier standard --format zip --output <临时目录>`。
3. 将 zip 内的 `markdown.md` 原样导入 `<文件名>.md`，`images/` 导入根目录 `images/`，`structured_content.json`、`middle_json.json`、`model_output.json` 导入 `mineru/`。
4. 生成 `conversion-manifest.json`，记录引擎、命令、模型语言、页数、页面结构块、图片、警告和链接校验结果。
5. 优先保留教材正文图、地图、图表、流程图、实验装置图、题图和无法可靠重建的表格图；不主动复制装饰背景。

MinerU 的原始 Markdown 通常没有页面注释（4.x 的 zip `markdown.md` 即如此）。此时必须保留 `mineru/structured_content.json` 或同等结构化结果，以页面记录提供追溯；不能为了添加页码而重新改写 MinerU 原文。页码追溯由 Stage 2 在格式化稿中用 `<!-- 来源页：N -->` 补足。

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

## Stage 4：拆分稿 Markdown 精修（可选）

拆分稿只是「切对了」，还不一定「能用」。扫描件 OCR 常留下以下病灶，需要单独一遍精修：

```bash
python study_skills/pdf-markdown/scripts/markdown_polish.py polish --dir <输出目录>/拆分/章节
python study_skills/pdf-markdown/scripts/markdown_polish.py check  --dir <输出目录>/拆分/章节
```

`polish` 的修复项：

- **图片路径**：拆分稿在 `拆分/<kind>/` 两层深处，图片却按一层写法引用 → 统一为 `../../images/`（可用 `--images-rel` 覆盖）；空 alt 按文件名补全为 `![图 p95-21]`。
- **HTML 表格**：`<table>`（含内嵌 `<img>`、colspan/rowspan）→ Markdown 表格。
- **表格列宽**：单元格内 LaTeX 竖线未转义会把一行切成多列 → 以分隔行为准对齐列宽，竖线转义成 `\|`；单列表格还原为列表。
- **表格公式**：单元格内裸露的数学符号补 `$...$`。
- **公式结构**：`$\begin{cases}...\end{cases}$` 等含多行结构的行内公式提升为独立 `$$` 块；`$A$$B$` 拆成 `$A$ $B$`。
- **标题层级**：`#` → `##` → `###` 压平，去重与文件名重复的正文标题。
- **列表化**：`(1)` `①` `（一）` 等教材编号 → Markdown 有序/无序列表；短编号行（`2. 集合间的基本关系`）提升为小节标题。
- **段落**：仅当上一行未以句末标点收尾时才合并被版面换行切断的段落。
- **元信息**：旧的 `> 所属/来源/...` 块换成 YAML frontmatter（title / book / pages / tags）。

铁律：

- 只做**可逆的结构与格式整理**，不改写正文措辞，不修正 OCR 识别错误；
- **裸 `<` 后紧跟字母必须处理**（插空格成 `< x`）：HTML 渲染器会把它当作未闭合标签起始，一路吞到下一个 `>`，导致大段内容消失、整页渲染崩坏；`<!-- -->` 注释内的 `<` 保留；数学环境内的 `<` 同样受影响；
- 数学片段里的 `\|` 要换成 `\mid`（`\|` 渲染成 ∥ 平行号，集合分隔符语义错误）；
- 空格清理必须保守——只动标点周围、连续空格和行尾，不删中文之间的单空格（否则「提示 集合是……」会粘成「提示集合是」）；
- 标题行不参与空格清理（否则「第一章 集合」会变成「第一章集合」）；
- 每次精修前自动备份到 `拆分/_优化前备份/`，可 diff 可回滚；
- `check` 必须 100% 通过：图片零断链、`$` 与 `$$` 成对、表格列宽一致、标题不跳级、无危险裸 `<`。

## Validation gate

执行：

```bash
python study_skills/pdf-markdown/scripts/pdf_markdown_pipeline.py validate --dir <输出目录>
```

必须同时满足：

- 原始稿、格式化稿、manifest 和拆分 README 存在；
- MinerU `structured_content.json` 页数与 manifest 页面记录一致；
- 原始稿、格式化稿和拆分稿的图片链接全部存在；
- 每张提取图片的引用状态、来源页和去重关系可从 manifest 追溯；
- 章节/单元标题没有因目录或页眉重复生成多个文档；
- 没有明显 `cid:`、重复艺术字、错序栏文本、孤立页脚或断裂题目关系；
- OCR、缺页、模型/命令失败、过滤图片和人工复核项均已记录。

如果质量不能确定，必须列出具体页码或章节，不能只写“转换完成”。

## Boundary

本技能只负责 PDF 原始转换、图片提取、格式化和单元/章节拆分。用户要求生成学习型章节笔记时，再使用 `$chapter-notes`；不得把整份教材转换稿直接当作正式学习笔记。
