import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INGESTION_PATH = ROOT / "scripts" / "pdf_ingestion.py"
CLI_PATH = ROOT / "scripts" / "ingest_pdf.py"


def load_ingestion():
    spec = importlib.util.spec_from_file_location("pdf_ingestion", INGESTION_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("pdf ingestion module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PdfIngestionPrimitiveTests(unittest.TestCase):
    def test_build_paths_use_category_title_and_slug(self):
        module = load_ingestion()
        paths = module.build_output_paths(
            markdown_root=Path("markdown"),
            books_root=Path("books"),
            category="商业管理",
            title="系统思考",
        )
        self.assertEqual(Path("markdown/商业管理/系统思考"), paths.markdown_dir)
        self.assertEqual(Path("books/系统思考"), paths.book_dir)

    def test_path_segment_rejects_escape(self):
        module = load_ingestion()
        for value in ("", ".", "..", "../商业", "/tmp/book", "book/name", "book\\name", "book\x00name"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.safe_segment(value)

    def test_sha256_file_is_stable(self):
        module = load_ingestion()
        with tempfile.TemporaryDirectory() as temp:
            pdf = Path(temp) / "book.pdf"
            pdf.write_bytes(b"book-pdf")
            self.assertEqual(
                "5c4d0fb52beccbc052ee87a57607e00d7519962ff5bc276950959c777d06797e",
                module.sha256_file(pdf),
            )

    def test_slugify_title_preserves_chinese_and_normalizes_whitespace(self):
        module = load_ingestion()
        self.assertEqual("系统思考-入门", module.slugify_title("系统思考  入门"))
        self.assertEqual("Deep-Learning系统", module.slugify_title("Deep Learning：系统"))

    def test_slugify_title_rejects_empty_or_punctuation_only(self):
        module = load_ingestion()
        for value in ("", "   ", "---", "!!!", "\x00"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.slugify_title(value)

    def test_output_paths_and_config_are_immutable(self):
        module = load_ingestion()
        paths = module.build_output_paths(Path("markdown"), Path("books"), "商业管理", "系统思考")
        with self.assertRaises(FrozenInstanceError):
            paths.book_dir = Path("other")
        config = module.IngestionConfig(
            pdf=Path("book.pdf"),
            markdown_root=Path("markdown"),
            books_root=Path("books"),
            category="商业管理",
            title="系统思考",
        )
        with self.assertRaises(FrozenInstanceError):
            config.title = "其他"

    def test_atomic_write_text_replaces_target_after_success(self):
        module = load_ingestion()
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "nested" / "manifest.txt"
            module.atomic_write_text(target, "第一次")
            self.assertEqual("第一次", target.read_text(encoding="utf-8"))
            module.atomic_write_text(target, "第二次")
            self.assertEqual("第二次", target.read_text(encoding="utf-8"))
            self.assertEqual([], list(target.parent.glob(".manifest.txt.*.tmp")))

    def test_json_helpers_round_trip_payload(self):
        module = load_ingestion()
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "nested" / "manifest.json"
            payload = {"title": "系统思考", "pages": 10, "tags": ["book"]}
            module.write_json(target, payload)
            self.assertEqual(payload, module.read_json(target))
            self.assertEqual(payload, json.loads(target.read_text(encoding="utf-8")))


class MinerUAdapterTests(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tempdir.name)
        self.module = load_ingestion()

    def tearDown(self):
        self._tempdir.cleanup()

    def test_locate_mineru_prefers_explicit_path(self):
        binary = self.root / "mineru"
        binary.write_text("#!/bin/sh\n", encoding="utf-8")
        binary.chmod(0o755)
        self.assertEqual(
            binary,
            self.module.locate_mineru(binary, project_root=self.root),
        )

    def test_find_mineru_auto_dir_requires_markdown_and_content_list(self):
        auto = self.root / "job" / "auto"
        auto.mkdir(parents=True)
        (auto / "book.md").write_text("# Book\n", encoding="utf-8")
        with self.assertRaises(self.module.IngestionError):
            self.module.find_mineru_auto_dir(self.root / "job")

    def test_build_mineru_command_is_explicit(self):
        command = self.module.build_mineru_command(
            Path("/bin/mineru"), Path("book.pdf"), Path("stage"), "pipeline", "ch"
        )
        self.assertEqual(
            ["/bin/mineru", "-p", "book.pdf", "-o", "stage", "-b", "pipeline", "-l", "ch"],
            command,
        )


class ConversionAssetTests(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tempdir.name)
        self.module = load_ingestion()
        self.markdown_dir = self.root / "markdown" / "商业管理" / "系统思考"
        self.config = self.module.IngestionConfig(
            pdf=self.root / "系统思考.pdf",
            markdown_root=self.root / "markdown",
            books_root=self.root / "books",
            category="商业管理",
            title="系统思考",
        )
        self.config.pdf.write_bytes(b"synthetic pdf")
        self.auto_dir = self.root / "auto"
        (self.auto_dir / "images").mkdir(parents=True)
        (self.auto_dir / "book.md").write_text(
            "# 系统思考\n\n![图 1](images/figure-1.png)\n", encoding="utf-8"
        )
        (self.auto_dir / "book_content_list_v2.json").write_text(
            '{"pages": []}\n', encoding="utf-8"
        )
        (self.auto_dir / "images" / "figure-1.png").write_bytes(b"figure")

    def tearDown(self):
        self._tempdir.cleanup()

    def test_import_mineru_output_copies_raw_assets_and_manifest(self):
        result = self.module.import_mineru_output(
            self.config, self.auto_dir, mineru_version="1.3.0"
        )
        self.assertEqual(self.markdown_dir / "系统思考.md", result.raw_path)
        self.assertTrue((self.markdown_dir / "images" / "figure-1.png").is_file())
        self.assertTrue(
            (self.markdown_dir / "mineru" / "book_content_list_v2.json").is_file()
        )
        self.assertEqual("系统思考", result.manifest["book"]["title"])
        self.assertEqual("商业管理", result.manifest["book"]["category"])

    def test_import_mineru_output_preserves_additional_json_under_mineru(self):
        (self.auto_dir / "layout.json").write_text('{"blocks": []}\n', encoding="utf-8")
        self.module.import_mineru_output(self.config, self.auto_dir, mineru_version="1.3.0")
        self.assertTrue((self.markdown_dir / "mineru" / "layout.json").is_file())

    def test_format_markdown_removes_page_footers_without_changing_content(self):
        raw = (
            "<!-- page: 1 -->\n"
            "系统思考\n\n"
            "第一段保持不变。\n\n"
            "![图 1](images/figure-1.png)\n\n"
            "Page 1\n\n"
            "<!-- page: 2 -->\n"
            "系统思考\n\n"
            "第二段保持不变。\n\n"
            "Page 2\n"
        )
        formatted, changes = self.module.format_markdown(raw)
        self.assertIn("第一段保持不变。", formatted)
        self.assertIn("第二段保持不变。", formatted)
        self.assertIn("![图 1](images/figure-1.png)", formatted)
        self.assertNotIn("系统思考\n", formatted)
        self.assertNotIn("Page 1", formatted)
        self.assertNotIn("Page 2", formatted)
        self.assertTrue(changes)

    def test_format_markdown_preserves_repeated_short_body_paragraphs(self):
        raw = "重要提醒\n\n正文一。\n\n重要提醒\n\n正文二。\n"
        formatted, changes = self.module.format_markdown(raw)
        self.assertEqual(2, formatted.count("重要提醒"))
        self.assertEqual([], changes)

    def test_format_markdown_preserves_nonboundary_page_like_body_lines(self):
        raw = "请参见 Page 10\n\n增长 · 2\n"
        formatted, changes = self.module.format_markdown(raw)
        self.assertIn("请参见 Page 10", formatted)
        self.assertIn("增长 · 2", formatted)
        self.assertEqual([], changes)

    def test_format_markdown_preserves_page_edge_prose_resembling_footers(self):
        raw = (
            "<!-- page: 1 -->\n"
            "正文引用 Page 10\n\n"
            "<!-- page: 2 -->\n"
            "正文比例 · 2\n"
        )
        formatted, changes = self.module.format_markdown(raw)
        self.assertIn("正文引用 Page 10", formatted)
        self.assertIn("正文比例 · 2", formatted)
        self.assertEqual([], changes)

    def test_split_chapters_ignores_table_of_contents_headings(self):
        formatted = (
            "# 目录\n\n"
            "## 第一章 系统\n\n"
            "## 第二章 反馈\n\n"
            "# 正文\n\n"
            "## 第一章 系统\n\n"
            "系统由相互作用的部分组成。\n\n"
            "## 第二章 反馈\n\n"
            "反馈会改变系统行为。\n"
        )
        chapter_paths = self.module.split_chapters(formatted, self.markdown_dir, "系统思考")
        self.assertEqual(2, len(chapter_paths))
        self.assertTrue((self.markdown_dir / "拆分" / "README.md").is_file())
        self.assertTrue((self.markdown_dir / "拆分" / "章节" / "README.md").is_file())
        self.assertIn("系统由相互作用", chapter_paths[0].read_text(encoding="utf-8"))
        self.assertIn("反馈会改变", chapter_paths[1].read_text(encoding="utf-8"))

    def test_split_chapters_exits_contents_for_a_top_level_body_chapter(self):
        formatted = (
            "# 目录\n\n"
            "## 第一章 系统\n\n"
            "## 第二章 反馈\n\n"
            "# 第一章 系统\n\n"
            "系统正文。\n\n"
            "# 第二章 反馈\n\n"
            "反馈正文。\n"
        )
        chapter_paths = self.module.split_chapters(formatted, self.markdown_dir, "系统思考")
        self.assertEqual(2, len(chapter_paths))
        self.assertIn("系统正文。", chapter_paths[0].read_text(encoding="utf-8"))
        self.assertIn("反馈正文。", chapter_paths[1].read_text(encoding="utf-8"))

    def test_split_chapter_rewrites_images_and_complete_output_validates(self):
        (self.markdown_dir / "images").mkdir(parents=True)
        (self.markdown_dir / "images" / "figure-1.png").write_bytes(b"figure")
        formatted = "## 第一章 系统\n\n![图 1](images/figure-1.png)\n"
        chapter_path = self.module.split_chapters(
            formatted, self.markdown_dir, "系统思考"
        )[0]
        self.assertIn(
            "![图 1](../../images/figure-1.png)",
            chapter_path.read_text(encoding="utf-8"),
        )
        self.assertEqual(0, self.module.validate_conversion(self.markdown_dir).blocking_count)

    def test_validate_conversion_reports_missing_image_as_blocking(self):
        self.markdown_dir.mkdir(parents=True)
        (self.markdown_dir / "系统思考.md").write_text(
            "![缺图](images/missing.png)\n", encoding="utf-8"
        )
        report = self.module.validate_conversion(self.markdown_dir)
        self.assertEqual("invalid", report.status)
        self.assertEqual(1, report.blocking_count)
        self.assertIn("missing_image", [issue.code for issue in report.issues])


class BookPackageInitializationTests(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tempdir.name)
        self.module = load_ingestion()
        self.markdown_dir = self.root / "markdown" / "商业管理" / "系统思考"
        self.chapter_dir = self.markdown_dir / "拆分" / "章节"
        (self.markdown_dir / "images").mkdir(parents=True)
        self.chapter_dir.mkdir(parents=True)
        (self.markdown_dir / "images" / "feedback.png").write_bytes(b"feedback")
        (self.markdown_dir / "images" / "unused.png").write_bytes(b"unused")
        (self.chapter_dir / "01-第一章 系统.md").write_text(
            "# 第一章 系统\n\n第一段。\n\n![反馈](../../images/feedback.png)\n\n第二段。\n",
            encoding="utf-8",
        )
        self._write_manifest(status="passed", blocking_count=0)

    def tearDown(self):
        self._tempdir.cleanup()

    def _write_manifest(
        self,
        status,
        blocking_count,
        sha256="a" * 64,
        title="系统思考",
        pdf="/sources/系统思考.pdf",
    ):
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        (self.markdown_dir / "conversion-manifest.json").write_text(
            json.dumps(
                {
                    "book": {"title": title, "category": "商业管理", "language": "ch"},
                    "source": {"pdf": pdf, "sha256": sha256},
                    "engine": {"name": "MinerU", "version": "1.3.0"},
                    "validation": {"status": status, "blocking_count": blocking_count},
                }
            ),
            encoding="utf-8",
        )

    def test_initialize_package_copies_staging_sources_and_referenced_assets(self):
        package = self.module.initialize_book_package(
            conversion_dir=self.markdown_dir,
            books_root=self.root / "books",
        )
        self.assertEqual(self.root / "books" / "系统思考", package)
        self.assertTrue((package / "manifest.yaml").is_file())
        source = package / "chapters" / "ch01" / "source.md"
        self.assertTrue(source.is_file())
        manifest = (package / "manifest.yaml").read_text(encoding="utf-8")
        self.assertIn("source-state: staging", manifest)
        self.assertIn("ingestion:", manifest)
        self.assertIn("<!-- locator: ch01-p001 -->\n第一段。", source.read_text(encoding="utf-8"))
        self.assertNotIn("source-state: sealed", source.read_text(encoding="utf-8"))
        self.assertTrue((package / "chapters" / "ch01" / "assets" / "feedback.png").is_file())
        self.assertFalse((package / "chapters" / "ch01" / "assets" / "unused.png").exists())
        self.assertIn("assets/feedback.png", source.read_text(encoding="utf-8"))
        self.assertIn("source_pdf_sha256: \"" + "a" * 64 + "\"", manifest)
        self.assertIn("gate_status: \"passed\"", manifest)

    def test_initialize_package_does_not_create_package_when_conversion_gate_fails(self):
        self._write_manifest(status="invalid", blocking_count=1)
        with self.assertRaises(self.module.IngestionError):
            self.module.initialize_book_package(self.markdown_dir, self.root / "books")


    def test_initialize_package_rejects_existing_package_with_different_pdf_hash(self):
        package = self.module.initialize_book_package(self.markdown_dir, self.root / "books")
        self._write_manifest(status="passed", blocking_count=0, sha256="b" * 64)
        with self.assertRaises(self.module.IngestionError):
            self.module.initialize_book_package(self.markdown_dir, self.root / "books")
        self.assertTrue(package.is_dir())

    def test_initialize_package_returns_complete_matching_package_without_overwrite(self):
        package = self.module.initialize_book_package(self.markdown_dir, self.root / "books")
        source = package / "chapters" / "ch01" / "source.md"
        source.write_text("preserved existing package\n", encoding="utf-8")
        self.assertEqual(
            package,
            self.module.initialize_book_package(self.markdown_dir, self.root / "books"),
        )
        self.assertEqual("preserved existing package\n", source.read_text(encoding="utf-8"))

    def test_add_stable_paragraph_ids_preserves_markdown_constructs(self):
        markdown = (
            "Heading\n=======\n\n"
            "- one\n- two\n\n"
            "| A | B |\n| - | - |\n| 1 | 2 |\n\n"
            "> quoted **text**\n\n"
            "```python\nprint('code')\n```\n\n"
            "A *paragraph* with a [link](https://example.com).\n"
        )
        result = self.module.add_stable_paragraph_ids(markdown, "ch01")
        self.assertIn("<!-- source-state: staging -->", result)
        self.assertIn("<!-- locator: ch01-p001 -->", result)
        self.assertIn("Heading\n=======", result)
        self.assertIn("- one\n- two", result)
        self.assertIn("| A | B |\n| - | - |\n| 1 | 2 |", result)
        self.assertIn("> quoted **text**", result)
        self.assertIn("```python\nprint('code')\n```", result)
        self.assertIn("A *paragraph* with a [link](https://example.com).", result)
        self.assertNotIn("<p id=", result)
        body = result.split("<!-- chapter: ch01 -->\n", 1)[1]
        self.assertEqual(
            markdown,
            re.sub(r"^<!-- locator: ch01-p\d{3} -->\n", "", body, flags=re.MULTILINE),
        )

    def test_add_stable_paragraph_ids_skips_code_and_list_continuations(self):
        markdown = (
            "开头安全段落。\n\n"
            "```text\n代码第一行\n\n代码第二行\n```\n\n"
            "    缩进代码第一行\n    缩进代码第二行\n\n"
            "- 列表项\n\n"
            "  列表续行段落。\n\n"
            "  仍属于列表续行。\n\n"
            "结尾安全段落。\n"
        )
        result = self.module.add_stable_paragraph_ids(markdown, "ch01")
        body = result.split("<!-- chapter: ch01 -->\n", 1)[1]
        self.assertEqual(
            markdown,
            re.sub(r"^<!-- locator: ch01-p\d{3} -->\n", "", body, flags=re.MULTILINE),
        )
        self.assertIn("<!-- locator: ch01-p001 -->\n开头安全段落。", result)
        self.assertIn("<!-- locator: ch01-p002 -->\n结尾安全段落。", result)
        protected = result[result.index("```text") : result.index("<!-- locator: ch01-p002 -->")]
        self.assertNotIn("<!-- locator:", protected)

    def test_add_stable_paragraph_ids_skips_multiline_html_comments_and_raw_blocks(self):
        markdown = (
            "前置安全段落。\n\n"
            "<!--\n注释中的第一行。\n\n注释中的第二行。\n-->\n\n"
            "<textarea>\n原始块第一行。\n\n原始块第二行。\n</textarea>\n\n"
            "后置安全段落。\n"
        )
        result = self.module.add_stable_paragraph_ids(markdown, "ch01")
        body = result.split("<!-- chapter: ch01 -->\n", 1)[1]
        self.assertEqual(
            markdown,
            re.sub(r"^<!-- locator: ch01-p\d{3} -->\n", "", body, flags=re.MULTILINE),
        )
        self.assertIn("<!-- locator: ch01-p001 -->\n前置安全段落。", result)
        self.assertIn("<!-- locator: ch01-p002 -->\n后置安全段落。", result)
        comment = result[result.index("<!--\n") : result.index("<textarea>")]
        textarea = result[result.index("<textarea>") : result.index("<!-- locator: ch01-p002 -->")]
        self.assertNotIn("<!-- locator:", comment)
        self.assertNotIn("<!-- locator:", textarea)

    def test_initialize_package_resolves_nonstandard_relative_chapter_asset(self):
        nested_asset = self.markdown_dir / "拆分" / "figures" / "nested.png"
        nested_asset.parent.mkdir(parents=True)
        nested_asset.write_bytes(b"nested")
        (self.chapter_dir / "01-第一章 系统.md").write_text(
            "# 第一章 系统\n\n![嵌套](../figures/nested.png)\n", encoding="utf-8"
        )
        package = self.module.initialize_book_package(self.markdown_dir, self.root / "books")
        source = (package / "chapters" / "ch01" / "source.md").read_text(encoding="utf-8")
        self.assertTrue((package / "chapters" / "ch01" / "assets" / "拆分" / "figures" / "nested.png").is_file())
        self.assertIn("assets/拆分/figures/nested.png", source)

    def test_initialize_package_copies_reference_style_chapter_asset(self):
        (self.markdown_dir / "images" / "reference.png").write_bytes(b"reference")
        (self.chapter_dir / "01-第一章 系统.md").write_text(
            "# 第一章 系统\n\n![引用图][system-figure]\n\n"
            "[system-figure]: ../../images/reference.png\n",
            encoding="utf-8",
        )
        package = self.module.initialize_book_package(self.markdown_dir, self.root / "books")
        source = (package / "chapters" / "ch01" / "source.md").read_text(encoding="utf-8")
        self.assertTrue((package / "chapters" / "ch01" / "assets" / "reference.png").is_file())
        self.assertIn("![引用图][system-figure]", source)
        self.assertIn("[system-figure]: assets/reference.png", source)

    def test_initialize_package_copies_shortcut_reference_chapter_asset(self):
        (self.markdown_dir / "images" / "shortcut.png").write_bytes(b"shortcut")
        (self.chapter_dir / "01-第一章 系统.md").write_text(
            "# 第一章 系统\n\n![shortcut-figure]\n\n"
            "[shortcut-figure]: ../../images/shortcut.png\n",
            encoding="utf-8",
        )
        package = self.module.initialize_book_package(self.markdown_dir, self.root / "books")
        source = (package / "chapters" / "ch01" / "source.md").read_text(encoding="utf-8")
        self.assertTrue((package / "chapters" / "ch01" / "assets" / "shortcut.png").is_file())
        self.assertIn("![shortcut-figure]", source)
        self.assertIn("[shortcut-figure]: assets/shortcut.png", source)

    def test_initialize_package_preserves_external_reference_images(self):
        (self.chapter_dir / "01-第一章 系统.md").write_text(
            "# 第一章 系统\n\n![远程][remote-image]\n![数据][data-image]\n\n"
            "[remote-image]: https://example.com/remote.png\n"
            "[data-image]: data:image/png;base64,AAAA\n",
            encoding="utf-8",
        )
        package = self.module.initialize_book_package(self.markdown_dir, self.root / "books")
        source = (package / "chapters" / "ch01" / "source.md").read_text(encoding="utf-8")
        self.assertIn("[remote-image]: https://example.com/remote.png", source)
        self.assertIn("[data-image]: data:image/png;base64,AAAA", source)
        self.assertFalse((package / "chapters" / "ch01" / "assets").exists())

    def test_initialize_package_rejects_missing_or_escaping_chapter_assets_without_package(self):
        outside = self.root / "outside.png"
        outside.write_bytes(b"outside")
        (self.chapter_dir / "01-第一章 系统.md").write_text(
            "# 第一章 系统\n\n![逃逸](../../../../outside.png)\n", encoding="utf-8"
        )
        with self.assertRaises(self.module.IngestionError):
            self.module.initialize_book_package(self.markdown_dir, self.root / "books")
        self.assertFalse((self.root / "books" / "系统思考").exists())

    def test_initialize_package_rejects_windows_absolute_chapter_assets(self):
        for target in (r"C:\\assets\\unsafe.png", r"\\\\server\\share\\unsafe.png"):
            with self.subTest(target=target):
                (self.chapter_dir / "01-第一章 系统.md").write_text(
                    f"# 第一章 系统\n\n![Windows]({target})\n", encoding="utf-8"
                )
                with self.assertRaises(self.module.IngestionError):
                    self.module.initialize_book_package(self.markdown_dir, self.root / "books")
                self.assertFalse((self.root / "books" / "系统思考").exists())
        (self.chapter_dir / "01-第一章 系统.md").write_text(
            "# 第一章 系统\n\n![绝对路径](/tmp/unsafe.png)\n", encoding="utf-8"
        )
        with self.assertRaises(self.module.IngestionError):
            self.module.initialize_book_package(self.markdown_dir, self.root / "books")
        self.assertFalse((self.root / "books" / "系统思考").exists())
        (self.chapter_dir / "01-第一章 系统.md").write_text(
            "# 第一章 系统\n\n![缺失](../../images/missing.png)\n", encoding="utf-8"
        )
        with self.assertRaises(self.module.IngestionError):
            self.module.initialize_book_package(self.markdown_dir, self.root / "books")
        self.assertFalse((self.root / "books" / "系统思考").exists())

    def test_initialize_package_is_atomic_for_later_empty_chapter(self):
        (self.chapter_dir / "02-第二章 空白.md").write_text("\n", encoding="utf-8")
        with self.assertRaises(self.module.IngestionError):
            self.module.initialize_book_package(self.markdown_dir, self.root / "books")
        self.assertFalse((self.root / "books" / "系统思考").exists())

    def test_initialize_package_copies_multiple_chapters_and_root_synthesis_templates(self):
        (self.chapter_dir / "02-第二章 反馈.md").write_text(
            "# 第二章 反馈\n\n反馈正文。\n", encoding="utf-8"
        )
        package = self.module.initialize_book_package(self.markdown_dir, self.root / "books")
        self.assertTrue((package / "BOOK.md").is_file())
        self.assertTrue((package / "synthesis" / "book-map.md").is_file())
        self.assertTrue((package / "chapters" / "ch02" / "source.md").is_file())

    def test_initialize_package_yaml_quotes_hostile_title_and_path(self):
        title = '系统: "思考"\nextra: true'
        pdf = 'C:\\books\\source: "unsafe"\nextra.pdf'
        self._write_manifest("passed", 0, title=title, pdf=pdf)
        package = self.module.initialize_book_package(self.markdown_dir, self.root / "books")
        manifest = (package / "manifest.yaml").read_text(encoding="utf-8")
        self.assertIn('title: "系统: \\"思考\\"\\nextra: true"', manifest)
        self.assertIn('"C:\\\\books\\\\source: \\"unsafe\\"\\nextra.pdf"', manifest)
        self.assertNotIn("\nextra: true\n", manifest)

    def test_initialize_package_normalizes_unreadable_existing_manifest_error(self):
        package = self.root / "books" / "系统思考"
        package.mkdir(parents=True)
        (package / "manifest.yaml").write_bytes(b"\xff")
        with self.assertRaises(self.module.IngestionError):
            self.module.initialize_book_package(self.markdown_dir, self.root / "books")


class PdfIngestionCliTests(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tempdir.name)

    def tearDown(self):
        self._tempdir.cleanup()

    def _run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(CLI_PATH), *arguments],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_help_lists_supported_commands(self):
        result = self._run_cli("--help")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("run", result.stdout)
        self.assertIn("import-mineru", result.stdout)
        self.assertIn("validate", result.stdout)

    def test_import_mineru_prints_markdown_and_book_output_directories(self):
        pdf = self.root / "系统思考.pdf"
        pdf.write_bytes(b"synthetic pdf")
        mineru_output = self.root / "mineru-output" / "auto"
        (mineru_output / "images").mkdir(parents=True)
        (mineru_output / "系统思考.md").write_text(
            "# 第一章 系统\n\n系统正文。\n\n![图 1](images/figure-1.png)\n",
            encoding="utf-8",
        )
        (mineru_output / "book_content_list_v2.json").write_text(
            '{"pages": []}\n', encoding="utf-8"
        )
        (mineru_output / "images" / "figure-1.png").write_bytes(b"figure")

        result = self._run_cli(
            "import-mineru",
            "--pdf",
            str(pdf),
            "--mineru-output",
            str(self.root / "mineru-output"),
            "--category",
            "商业管理",
            "--title",
            "系统思考",
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn(str((self.root / "markdown" / "商业管理" / "系统思考").resolve()), result.stdout)
        self.assertIn(str((self.root / "books" / "系统思考").resolve()), result.stdout)


if __name__ == "__main__":
    unittest.main()
