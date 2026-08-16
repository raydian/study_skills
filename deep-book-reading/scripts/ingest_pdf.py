"""Command-line entry point for the MinerU PDF ingestion workflow."""

import argparse
import json
import sys
import tempfile
from pathlib import Path

from pdf_ingestion import (
    IngestionConfig,
    IngestionError,
    ensure_package_target_compatible,
    find_mineru_auto_dir,
    import_mineru_output,
    initialize_book_package,
    reuse_existing_conversion,
    run_mineru,
    validate_conversion,
)


def _config_from_args(args: argparse.Namespace) -> IngestionConfig:
    root = Path.cwd()
    config = IngestionConfig(
        pdf=Path(args.pdf),
        category=args.category,
        title=args.title,
        markdown_root=root / "markdown",
        books_root=root / "books",
        language=getattr(args, "language", "ch"),
        mineru_bin=(
            Path(args.mineru_bin) if getattr(args, "mineru_bin", None) else None
        ),
        work_root=root,
        conflict_policy=getattr(args, "conflict_policy", "reject"),
    )
    try:
        config.paths
    except (TypeError, ValueError) as exc:
        raise IngestionError(f"Invalid category or title: {exc}") from exc
    return config


def _validation_payload(report) -> dict[str, object]:
    return {
        "status": report.status,
        "blocking_count": report.blocking_count,
        "issues": [
            {"code": issue.code, "message": issue.message, "path": str(issue.path)}
            for issue in report.issues
        ],
    }


def _import_and_initialize(
    config: IngestionConfig,
    auto_dir: Path,
    mineru_version: str,
    *,
    mineru_result=None,
) -> tuple[Path, Path]:
    keywords = {}
    if mineru_result is not None:
        keywords = {
            "mineru_binary": mineru_result.binary,
            "command": mineru_result.command,
            "started_at": mineru_result.started_at,
            "completed_at": mineru_result.completed_at,
            "source_fingerprint": mineru_result.source_fingerprint,
        }
    conversion = import_mineru_output(
        config,
        auto_dir,
        mineru_version,
        conflict_policy=config.conflict_policy,
        **keywords,
    )
    report = validate_conversion(conversion.manifest_path.parent)
    if report.blocking_count:
        raise IngestionError(
            f"Conversion validation failed with {report.blocking_count} blocking issue(s)"
        )

    package = initialize_book_package(conversion.manifest_path.parent, config.books_root)
    return conversion.manifest_path.parent, package


def _run(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    ensure_package_target_compatible(config)
    existing = reuse_existing_conversion(config)
    if existing is not None:
        package = initialize_book_package(existing.manifest_path.parent, config.books_root)
        print(f"markdown_dir: {existing.manifest_path.parent.resolve()}")
        print(f"book_dir: {package.resolve()}")
        return 0
    staging_dir = Path(
        tempfile.mkdtemp(prefix=f".{config.paths.slug}-mineru-", dir=config.work_root)
    )
    mineru = run_mineru(config, staging_dir)
    markdown_dir, package = _import_and_initialize(
        config, mineru.auto_dir, mineru.version, mineru_result=mineru
    )
    print(f"markdown_dir: {markdown_dir.resolve()}")
    print(f"book_dir: {package.resolve()}")
    return 0


def _import(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    ensure_package_target_compatible(config)
    existing = reuse_existing_conversion(config)
    if existing is not None:
        package = initialize_book_package(existing.manifest_path.parent, config.books_root)
        print(f"markdown_dir: {existing.manifest_path.parent.resolve()}")
        print(f"book_dir: {package.resolve()}")
        return 0
    markdown_dir, package = _import_and_initialize(
        config, find_mineru_auto_dir(Path(args.mineru_output)), "unknown"
    )
    print(f"markdown_dir: {markdown_dir.resolve()}")
    print(f"book_dir: {package.resolve()}")
    return 0


def _validate(args: argparse.Namespace) -> int:
    report = validate_conversion(Path(args.conversion_dir))
    print(json.dumps(_validation_payload(report), ensure_ascii=False, indent=2))
    return 1 if report.blocking_count else 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ingest_pdf.py")
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("run", help="run MinerU and initialize a book package")
    run.add_argument("--pdf", required=True, metavar="PATH")
    run.add_argument("--category", required=True, metavar="CATEGORY")
    run.add_argument("--title", required=True, metavar="TITLE")
    run.add_argument("--language", default="ch", metavar="LANGUAGE")
    run.add_argument("--mineru-bin", metavar="PATH")
    run.add_argument(
        "--conflict-policy", choices=("reject", "replace"), default="reject"
    )
    run.set_defaults(handler=_run)

    imported = commands.add_parser(
        "import-mineru", help="import an existing complete MinerU output"
    )
    imported.add_argument("--pdf", required=True, metavar="PATH")
    imported.add_argument("--mineru-output", required=True, metavar="PATH")
    imported.add_argument("--category", required=True, metavar="CATEGORY")
    imported.add_argument("--title", required=True, metavar="TITLE")
    imported.add_argument(
        "--conflict-policy", choices=("reject", "replace"), default="reject"
    )
    imported.set_defaults(handler=_import)

    validate = commands.add_parser(
        "validate", help="validate a converted Markdown directory"
    )
    validate.add_argument("--conversion-dir", required=True, metavar="PATH")
    validate.set_defaults(handler=_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except IngestionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
