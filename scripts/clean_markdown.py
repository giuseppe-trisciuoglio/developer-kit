#!/usr/bin/env python3
# Script per pulire file Markdown generati da conversione web->md
# Crea backup dei file originali in una directory .md_clean_backups/<timestamp>/

import argparse
import os
import re
import shutil
from pathlib import Path
from datetime import datetime
import difflib

# Patterns di pulizia
RE_SCRIPT = re.compile(r"<script[\s\S]*?</script>", re.IGNORECASE)
RE_STYLE = re.compile(r"<style[\s\S]*?</style>", re.IGNORECASE)
RE_COMMENT = re.compile(r"<!--([\s\S]*?)-->")
RE_TAG = re.compile(r"<[^>]+>")
RE_ANCHOR_BRACE = re.compile(r"\{#[-a-zA-Z0-9_]+\}")
RE_TOC_TOKEN = re.compile(r"(^\s*\[toc\]\s*$)|(^\s*Table of contents\s*$)|(^\s*Contents\s*$)", re.IGNORECASE|re.MULTILINE)
RE_PERMALINK = re.compile(r"^\s*Permalink\s*$", re.IGNORECASE|re.MULTILINE)
RE_EDIT_ON = re.compile(r"Edit on GitHub|View on GitHub|Edit this page|Open in GitHub", re.IGNORECASE)
RE_BACKTOTOP = re.compile(r"Back to top|Back to TOC|Back to Contents", re.IGNORECASE)
RE_COPYRIGHT = re.compile(r"©|Copyright|All rights reserved", re.IGNORECASE)
RE_MULTIBLANK = re.compile(r"\n{3,}")
RE_TRAILING_WS = re.compile(r"[ \t]+$", re.MULTILINE)
RE_DATA_IMAGE = re.compile(r"!\[[^\]]*\]\(data:image[^)]+\)", re.IGNORECASE)
RE_PILCROW = re.compile(r"¶")
RE_HEADING_SPACING = re.compile(r"(#+ .+?)\n{2,}")
RE_HTML_ENTITY = re.compile(r"&nbsp;|&amp;|&lt;|&gt;|&quot;|&apos;")

SKIP_DIRS = {'.git', '.github', 'node_modules', '.venv', 'venv'}


def clean_text(text: str) -> str:
    orig = text
    # Remove script/style blocks
    text = RE_SCRIPT.sub('', text)
    text = RE_STYLE.sub('', text)
    # Remove HTML comments
    text = RE_COMMENT.sub('', text)
    # Remove HTML entities (leave basic replacements)
    text = text.replace('&nbsp;', ' ')
    # Remove data-image embeds
    text = RE_DATA_IMAGE.sub('', text)
    # Remove common "edit/view" and permalinks lines
    text = RE_TOC_TOKEN.sub('', text)
    text = RE_PERMALINK.sub('', text)
    text = RE_EDIT_ON.sub('', text)
    text = RE_BACKTOTOP.sub('', text)
    text = RE_COPYRIGHT.sub('', text)
    # Remove anchor brace tokens like {#some-id}
    text = RE_ANCHOR_BRACE.sub('', text)
    # Remove leftover HTML tags
    text = RE_TAG.sub('', text)
    # Remove pilcrow or other isolated weird chars
    text = RE_PILCROW.sub('', text)
    # Remove common HTML entities
    text = RE_HTML_ENTITY.sub(lambda m: {'&amp;':'&','&lt;':'<','&gt;':'>','&quot;':'"','&apos;':"'"}[m.group(0)], text)
    # Trim trailing spaces on each line
    text = RE_TRAILING_WS.sub('', text)
    # Collapse multiple blank lines to max two
    text = RE_MULTIBLANK.sub('\n\n', text)
    # Ensure single blank line after headings
    text = RE_HEADING_SPACING.sub(lambda m: m.group(1) + '\n\n', text)
    # Final strip
    text = text.strip() + '\n'

    return text


def should_process(path: Path) -> bool:
    if path.suffix.lower() != '.md':
        return False
    parts = set(path.parts)
    if parts & SKIP_DIRS:
        return False
    return True


def gather_md_files(root: Path):
    for p in root.rglob('*.md'):
        if should_process(p):
            yield p


def backup_file(src: Path, backup_root: Path):
    try:
        rel = src.relative_to(ROOT)
    except Exception:
        try:
            rel = src.relative_to(Path.cwd())
        except Exception:
            rel = Path(src.name)
    dest = backup_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clean Markdown files generated from web pages')
    parser.add_argument('--root', '-r', default='.', help='Repository root to scan')
    parser.add_argument('--apply', '-a', action='store_true', help='Apply changes in-place (default: dry-run)')
    parser.add_argument('--backup-dir', '-b', default=None, help='Optional backup directory root')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output with diff preview')
    parser.add_argument('--max-diff-lines', type=int, default=40, help='Max diff lines to show per file in verbose mode')
    args = parser.parse_args()

    ROOT = Path(args.root).resolve()
    md_files = list(gather_md_files(ROOT))
    print(f"Scansionati {len(md_files)} file markdown sotto: {ROOT}")
    if not md_files:
        print('No markdown files found to process under', ROOT)
        exit(0)

    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    if args.backup_dir:
        backup_root = Path(args.backup_dir)
    else:
        backup_root = ROOT / ('.md_clean_backups_' + timestamp)
    if args.apply:
        backup_root.mkdir(parents=True, exist_ok=True)

    summary = []
    for p in md_files:
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            try:
                text = p.read_text(encoding='latin-1')
            except Exception as e:
                print('SKIP (read error):', p, e)
                continue
        cleaned = clean_text(text)
        if cleaned != text:
            summary.append((p, text, cleaned))
        else:
            if args.verbose:
                # show small diagnostic when verbose and no change
                if len(text) > 2000:
                    print(f" - OK (no change)  : {p} (size {len(text)} bytes)")
                else:
                    print(f" - OK (no change)  : {p}")

    if not summary:
        print('Dry-run: nessuna modifica necessaria su', len(md_files), 'file markdown scansionati.')
        exit(0)

    print('Found', len(summary), 'file(s) that would be modified:')
    for p, old, new in summary:
        print(' -', p)
        if args.verbose:
            old_lines = old.splitlines(keepends=True)
            new_lines = new.splitlines(keepends=True)
            diff = list(difflib.unified_diff(old_lines, new_lines, fromfile=str(p) + ':original', tofile=str(p) + ':cleaned'))
            if diff:
                limited = diff[:args.max_diff_lines]
                print(''.join(limited))
                if len(diff) > args.max_diff_lines:
                    print(f"...diff truncated ({len(diff)} lines total), increase --max-diff-lines to see more...\n")

    if not args.apply:
        print('\nEsegui di nuovo con --apply per applicare le modifiche. (Verranno creati backup in', backup_root, ')')
        exit(0)

    # Apply changes with backups
    applied = 0
    for p, old, new in summary:
        try:
            dest = backup_file(p, backup_root)
            print(f'Backed up {p} -> {dest}')
            p.write_text(new, encoding='utf-8')
            print(f'Wrote cleaned file: {p}')
            applied += 1
        except Exception as e:
            print(f'ERROR applying change to {p}: {e}')

    print('Applied changes to', applied, 'file(s). Backups stored in', backup_root)
