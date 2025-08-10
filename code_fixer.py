import argparse
import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple

import subprocess

try:
    import autopep8  # type: ignore
except Exception as import_error:  # pragma: no cover
    autopep8 = None  # Will be validated at runtime


IGNORED_DIR_NAMES = {".git", "__pycache__", ".venv", "venv", ".mypy_cache", ".pytest_cache", ".idea", ".vscode"}


def discover_python_files(target_path: Path) -> List[Path]:
    if target_path.is_file() and target_path.suffix == ".py":
        return [target_path]
    if target_path.is_dir():
        python_files: List[Path] = []
        for root, dirs, files in os.walk(target_path):
            # prune ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORED_DIR_NAMES]
            for filename in files:
                if filename.endswith(".py"):
                    python_files.append(Path(root) / filename)
        return python_files
    return []


def check_syntax(file_path: Path) -> Tuple[bool, str]:
    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        ast.parse(source)
        return True, ""
    except SyntaxError as exc:  # pragma: no cover
        return False, f"{file_path}:{exc.lineno}:{exc.offset} SyntaxError: {exc.msg}"


def run_pylint(file_paths: List[Path]) -> str:
    if not file_paths:
        return ""
    cmd = [sys.executable, "-m", "pylint", "--output-format=text", *[str(p) for p in file_paths]]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()
    return "\n".join([s for s in [stdout, stderr] if s])


def run_flake8(file_paths: List[Path]) -> str:
    if not file_paths:
        return ""
    # flake8 can accept directories or files; pass files for consistency
    cmd = [sys.executable, "-m", "flake8", "--format=default", *[str(p) for p in file_paths]]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()
    return "\n".join([s for s in [stdout, stderr] if s])


def apply_autopep8(file_paths: List[Path], aggressive: int, max_line_length: int, write_in_place: bool = True) -> int:
    if autopep8 is None:
        raise RuntimeError("autopep8 is not installed. Please install it with: pip install autopep8")

    total_modified = 0
    for path in file_paths:
        original = path.read_text(encoding="utf-8", errors="ignore")
        fixed = autopep8.fix_code(
            original,
            options={
                "aggressive": aggressive,
                "max_line_length": max_line_length,
            },
        )
        if fixed != original:
            total_modified += 1
            if write_in_place:
                path.write_text(fixed, encoding="utf-8")
    return total_modified


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze Python files with pylint/flake8 and optionally auto-fix style issues with autopep8.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to a Python file or directory (default: current directory)",
    )
    parser.add_argument(
        "--analyzer",
        choices=["pylint", "flake8"],
        default="pylint",
        help="Which analyzer to use (default: pylint)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply autopep8 fixes before re-running analyzer",
    )
    parser.add_argument(
        "--aggressive",
        type=int,
        default=1,
        help="autopep8 aggressive level (0-2). Default: 1",
    )
    parser.add_argument(
        "--max-line-length",
        type=int,
        default=120,
        help="Maximum allowed line length for autopep8 (default: 120)",
    )
    parser.add_argument(
        "--skip-syntax-check",
        action="store_true",
        help="Skip AST syntax check before analysis",
    )
    parser.add_argument(
        "--allow-fix-with-syntax-errors",
        action="store_true",
        help="Allow running autopep8 even if syntax errors are detected",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Do not prompt; respect flags only",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = Path(args.path).resolve()
    files = discover_python_files(target)

    if not files:
        print(f"No Python files found at: {target}")
        return 1

    print(f"Discovered {len(files)} Python file(s) under: {target}")

    if not args.skip_syntax_check:
        syntax_errors: List[str] = []
        for f in files:
            ok, err = check_syntax(f)
            if not ok:
                syntax_errors.append(err)
        if syntax_errors:
            print("Syntax errors detected:\n" + "\n".join(syntax_errors))
            if args.fix and args.allow_fix_with_syntax_errors:
                print("Proceeding to run autopep8 despite syntax errors (per flag).")
            else:
                print("Aborting analysis. Fix syntax errors first or pass --skip-syntax-check or --allow-fix-with-syntax-errors with --fix.")
                return 2

    print(f"Running analyzer: {args.analyzer} ...")
    initial_report = run_pylint(files) if args.analyzer == "pylint" else run_flake8(files)
    if initial_report:
        print("\n=== Initial analysis report ===\n")
        print(initial_report)
    else:
        print("\nNo issues found by analyzer.")

    should_fix = args.fix
    if not should_fix and not args.non_interactive:
        try:
            response = input("\nApply autopep8 fixes now? (y/N) ").strip().lower()
            should_fix = response == "y"
        except EOFError:
            should_fix = False

    if should_fix:
        print("\nApplying autopep8 fixes...")
        try:
            changed = apply_autopep8(
                files,
                aggressive=args.aggressive,
                max_line_length=args.max_line_length,
                write_in_place=True,
            )
            print(f"autopep8 modified {changed} file(s).")
        except Exception as exc:  # pragma: no cover
            print(f"autopep8 failed: {exc}")
            return 3

        print(f"\nRe-running analyzer: {args.analyzer} ...")
        final_report = run_pylint(files) if args.analyzer == "pylint" else run_flake8(files)
        if final_report:
            print("\n=== Post-fix analysis report ===\n")
            print(final_report)
        else:
            print("\nNo issues found by analyzer after fixes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


