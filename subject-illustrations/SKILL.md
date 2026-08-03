---
name: subject-illustrations
agent_created: true
description: Generate and insert subject-consistent educational illustrations for Markdown study notes from 图片描述 HTML comments. Use when the user asks to create 学科图片插图, generate images from note image annotations, insert illustrations into chapter notes, keep image comments as captions/prompts, save assets beside the document in an images directory, or compress generated images under 1MB.
---

# Subject Illustrations

## Overview

Generate learning illustrations from Markdown image comments and insert them back into the same note. Use the `imagegen` skill for bitmap generation, use each `<!-- 图片描述：... -->` block as the prompt source, save images under an `images/` directory beside the Markdown file, and keep each original image comment directly below the inserted image.

## Required Inputs

- One Markdown file or a directory of Markdown files.
- A subject, inferred from the path when possible, such as `数学`, `物理`, `化学`, `生物`, `语文`, `英语`, `历史`, or `地理`.
- Existing image comments in this exact shape:

```markdown
<!-- 图片描述：... -->
```

If no image comments exist, stop and ask the user to first add or generate image comments.

## Workflow

1. Read this skill and `references/subject-styles.md`.
2. Use `scripts/scan_image_comments.py` to list image comments and detect already-inserted images.
3. Decide a consistent subject style from `references/subject-styles.md`; apply that same style to every prompt in the same subject.
4. For each unprocessed image comment:
   - Use the comment content as the primary generation description.
   - Append the subject style, image purpose, and a constraint that labels/formulas must be clean and legible.
   - Use the `imagegen` skill and built-in image generation tool.
   - Move or copy the selected generated image into an `images/` directory beside the Markdown file.
   - Name the file deterministically from the Markdown basename and comment order, such as `1.1-集合的概念-图01.webp`.
   - Compress the image with `scripts/compress_image.py` so the final file is under 1MB whenever possible.
   - Insert Markdown image syntax immediately above the original comment.
   - Keep the original image comment immediately below the image. Do not delete or rewrite the comment unless the user explicitly asks.
5. Validate every edited file:
   - each generated file exists;
   - image references are relative paths;
   - every original image comment remains;
   - each image comment has exactly one nearby image above it unless multiple variants were requested;
   - each image is under 1MB or the final response explains why it could not be compressed further.

## Insertion Format

Use this shape:

```markdown
![简短图片说明](images/<filename>.webp)
<!-- 图片描述：原始详细提示词，保留不删除。 -->
```

Rules:

- Put the image immediately above the comment it was generated from.
- Use a concise alt text derived from the comment topic, not the full prompt.
- Use relative paths from the Markdown file to the image.
- Do not place generated images in the project root or global assets folder unless the user explicitly requests that.
- Do not overwrite an existing image unless the user explicitly asks; use the next available `图NN` number.

## Prompt Construction

Use the image comment as the prompt core. Wrap it like this:

```text
Use case: scientific-educational
Asset type: Markdown chapter-note illustration
Primary request: <exact image comment content without the HTML delimiters>
Subject style: <style from references/subject-styles.md>
Composition: prioritize a knowledge structure diagram, process diagram, relationship map, method path, microscopic view, real-world operation mechanism, or problem-solving pathway according to the subject and the comment. Use ordinary illustrative scenes only as supporting context.
Text and labels: Chinese labels are allowed only when useful; formulas and symbols must be clean, readable, and consistent with the note.
Consistency: match the same subject style used for the other images in this subject.
```

Do not invent extra knowledge that conflicts with the comment or the note. If the comment is too vague to generate a useful image, improve the prompt only by using the nearby paragraph context and preserve the original educational intent.

## Illustration Purpose

Treat images as learning diagrams first, decorative illustrations second.

- Prefer knowledge structure diagrams, concept relationship maps, method flowcharts, cause-effect chains, comparison diagrams, microscopic mechanism diagrams, real-world operation diagrams, experiment/process diagrams, timeline maps, text-structure maps, or problem-solving path diagrams.
- Use a contextual scene only when it helps explain where the knowledge appears in the real world; the scene must include labels, arrows, structure, or process marks that explain the knowledge.
- Make every image answer at least one learning question: what is related to what, how the process works, how to judge a problem, how to solve it, what changes over time, what is happening at microscopic/real-world scale, or where evidence appears.
- Avoid images that merely decorate the page, repeat the title, or show a generic object without explaining the current knowledge point.

## Image Size And Compression

- Prefer WebP for diagrams and illustrations.
- Keep each final image under 1MB.
- Use `scripts/compress_image.py <input> --output <output>` after generation.
- If compression below 1MB harms legibility, keep the smallest legible version and report the file path and size.
- For label-heavy diagrams, legibility is more important than aggressive compression.

## Batch Behavior

For a directory:

- Process Markdown files in stable sorted order.
- Keep the same subject style across all files in that subject.
- Skip comments that already have a local image immediately above them unless the user asks to regenerate.
- Report generated, skipped, and failed counts.

## Safety And Quality

- Do not remove comments; comments are both the image prompt record and the caption source.
- Do not generate unrelated decorative images.
- Do not vary art styles within one subject.
- Do not use dark, low-contrast, blurred, or cinematic styles for learning diagrams.
- Prefer diagrams that enrich and complete the explanation of the current knowledge point: structure, relationship, process, method, mechanism, real-world operation, microscopic view, or answer path.
- After insertion, read the edited Markdown around each insertion to ensure the image is in the intended location.

## Resources

- `references/subject-styles.md`: subject style constraints.
- `scripts/scan_image_comments.py`: list comment blocks and insertion status.
- `scripts/compress_image.py`: convert/compress generated images to under 1MB where possible.
