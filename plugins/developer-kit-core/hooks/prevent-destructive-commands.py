#!/usr/bin/env python3
"""Destructive Command Prevention Hook for Claude Code.

Prevents execution of Bash commands that target paths outside the working
directory or match a blacklist of destructive operations.

Hook event: PreToolUse (Bash)
Input:  JSON via stdin  { "tool_name": "Bash", "tool_input": { "command": "..." } }
Output: Exit 0 = allow | Exit 2 = block (stderr shown to Claude)

Zero external dependencies — pure Python 3 standard library only.
"""

import json
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Optional

# ─── Blacklist Configuration ───────────────────────────────────────────────────

# Commands whose path arguments are validated against the working directory.
PATH_SENSITIVE_COMMANDS: frozenset[str] = frozenset(
    {"rm", "unlink", "rmdir", "shred", "del", "erase"}
)

# Commands that read file contents (used to detect access to sensitive files).
FILE_READING_COMMANDS: frozenset[str] = frozenset(
    {
        "cat", "less", "more", "head", "tail", "grep", "egrep", "fgrep",
        "awk", "sed", "cut", "sort", "uniq", "xxd", "hexdump", "strings",
        "base64", "openssl", "jq", "yq", "bat", "tac", "nl", "od", "rev",
    }
)

# Sensitive file patterns (files that should not be read).
SENSITIVE_FILE_PATTERNS: tuple[str, ...] = (
    # Environment files
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".env.test",
    ".env.staging",
    ".envrc",
    # SSH keys
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa.pub",
    "id_dsa.pub",
    "id_ecdsa.pub",
    "id_ed25519.pub",
    "authorized_keys",
    "known_hosts",
    # AWS credentials
    "credentials",
    "config",
    # Database credentials
    ".pgpass",
    ".my.cnf",
    ".netrc",
    # NPM/Package registry credentials
    ".npmrc",
    ".pypirc",
    "pip.conf",
    # Other secrets
    ".htpasswd",
    "vault-password",
    "secret",
    "secrets",
    "secret.json",
    "secrets.json",
    "secret.yaml",
    "secrets.yaml",
    "secret.yml",
    "secrets.yml",
    # Private keys (various formats)
    ".key",
    ".pem",
    ".p12",
    ".pfx",
    ".pkcs12",
    "private_key",
    "private-key",
)

# AWS CLI destructive sub-commands (matched as "<service> <operation>").
AWS_DESTRUCTIVE_SUBCOMMANDS: frozenset[str] = frozenset(
    {
        "s3 rm",
        "s3 mv",
        "s3 rb",
        "s3api delete-object",
        "s3api delete-objects",
        "s3api delete-bucket",
        "ec2 terminate-instances",
        "ec2 delete-security-group",
        "ec2 delete-vpc",
        "ec2 delete-subnet",
        "ec2 delete-volume",
        "ec2 delete-snapshot",
        "ec2 delete-key-pair",
        "rds delete-db-instance",
        "rds delete-db-cluster",
        "rds delete-db-snapshot",
        "rds delete-db-cluster-snapshot",
        "rds delete-db-parameter-group",
        "rds delete-db-subnet-group",
        "rds delete-db-security-group",
        "rds delete-global-cluster",
        "dynamodb delete-table",
        "lambda delete-function",
        "lambda delete-alias",
        "lambda delete-event-source-mapping",
        "lambda delete-layer-version",
        "lambda delete-provisioned-concurrency-config",
        "lambda delete-function-concurrency",
        "lambda delete-function-url-config",
        "lambda delete-code-signing-config",
        "iam delete-user",
        "iam delete-role",
        "iam delete-policy",
        "cloudformation delete-stack",
        "cloudformation delete-stack-instances",
        "cloudformation delete-stack-set",
        "cloudformation delete-change-set",
        "eks delete-cluster",
        "ecs delete-cluster",
        "ecs delete-service",
        "secretsmanager delete-secret",
        "kms schedule-key-deletion",
        "kms disable-key",
        "sns delete-topic",
        "sqs delete-queue",
    }
)

# Docker destructive sub-commands.
DOCKER_DESTRUCTIVE_SUBCOMMANDS: frozenset[str] = frozenset(
    {"rm", "rmi"}
)
DOCKER_DESTRUCTIVE_COMPOUND: frozenset[str] = frozenset(
    {
        # Modern canonical forms (docker <object> rm)
        "container rm",
        "image rm",
        "volume rm",
        "network rm",
        # Prune operations
        "container prune",
        "image prune",
        "volume prune",
        "network prune",
        "system prune",
        "builder prune",
    }
)

# Wrapper commands that delegate to a real command (skip them in analysis).
# These pass the real command as the very next token (e.g. sudo rm, env -i rm).
WRAPPER_COMMANDS: frozenset[str] = frozenset(
    {"sudo", "env", "nice", "nohup", "timeout", "ionice", "time"}
)

# Commands that execute their first non-flag positional argument as a shell command.
# Unlike WRAPPER_COMMANDS, these take a quoted command string that must be retokenized.
QUOTED_COMMAND_WRAPPERS: frozenset[str] = frozenset({"watch", "strace", "ltrace"})

# Shell invocation commands (recurse into -c argument).
SHELL_COMMANDS: frozenset[str] = frozenset({"bash", "sh", "zsh", "fish", "dash", "ksh"})

# Commands that pipe their arguments as a new command.
DELEGATION_COMMANDS: frozenset[str] = frozenset({"xargs", "parallel"})

# find flags that delegate execution.
FIND_EXEC_FLAGS: frozenset[str] = frozenset({"-exec", "-execdir", "-ok", "-okdir"})

# Shell operator tokens (not commands).
SHELL_OPERATORS: frozenset[str] = frozenset(
    {"|", ";", "&&", "||", "&", "(", ")", "{", "}", ">", "<", ">>", "<<", "2>", "2>>"}
)


# ─── Path Utilities ────────────────────────────────────────────────────────────


def _expand_tilde(path: str) -> str:
    """Expand leading tilde in a path string."""
    if path == "~":
        return str(Path.home())
    if path.startswith("~/"):
        return str(Path.home()) + path[1:]
    # ~username/ — treat as a path under /home, cannot verify safely
    if path.startswith("~"):
        username = path[1:].split("/")[0]
        return str(Path("/home") / username)
    return path


def _has_unresolvable_parts(path: str) -> bool:
    """Return True if the path contains shell variables, globs, or runtime placeholders.

    Handles:
    - $VAR and ${VAR} / $(cmd) forms
    - Glob characters: *, ?, [
    - find/xargs placeholder: {}  (expands to runtime-determined paths)
    """
    return bool(re.search(r"\$[{(]?\w?|\*|\?|\[", path)) or path == "{}"


def _resolve_path(path: str, cwd: str) -> Optional[str]:
    """Resolve path to absolute form; returns None if unresolvable."""
    path = _expand_tilde(path)
    if _has_unresolvable_parts(path):
        return None
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(cwd, path))


def _is_outside_cwd(path: str, cwd: str) -> tuple[bool, str]:
    """Return (is_outside, reason) for the given path relative to cwd."""
    if _has_unresolvable_parts(path):
        return True, f"unresolvable variable or glob in path: {path!r}"

    resolved = _resolve_path(path, cwd)
    if resolved is None:
        return True, f"cannot safely resolve path: {path!r}"

    cwd_prefix = cwd.rstrip("/") + "/"
    if resolved == cwd.rstrip("/") or (resolved + "/").startswith(cwd_prefix):
        return False, ""

    return True, f"{resolved!r} is outside working directory {cwd!r}"


# ─── Tokenizer ─────────────────────────────────────────────────────────────────


def _tokenize(command: str) -> list[str]:
    """Tokenize a shell command with proper handling of pipes, chains and quotes.

    shlex with posix=True splits ``$HOME`` into ``['$', 'HOME']``.
    This function reassembles such pairs back into ``['$HOME']`` so that
    variable-containing arguments are detected as unresolvable paths.
    """
    try:
        lexer = shlex.shlex(command, punctuation_chars=True, posix=True)
        lexer.whitespace_split = False
        raw = list(lexer)
    except ValueError:
        return command.split()

    result: list[str] = []
    i = 0
    while i < len(raw):
        tok = raw[i]
        # Reassemble $VAR or ${VAR} split by shlex punctuation handling
        if tok == "$" and i + 1 < len(raw):
            nxt = raw[i + 1]
            if nxt and (nxt[0].isalnum() or nxt[0] in "_{("):
                result.append("$" + nxt)
                i += 2
                continue
        # Reassemble find/xargs {} placeholder split into ['{', '}']
        if tok == "{" and i + 1 < len(raw) and raw[i + 1] == "}":
            result.append("{}")
            i += 2
            continue
        result.append(tok)
        i += 1
    return result


# ─── Recursive Command Checker ─────────────────────────────────────────────────


def _check_tokens(tokens: list[str], cwd: str, depth: int = 0) -> tuple[bool, str]:
    """Recursively check a token list for dangerous commands.

    Returns (is_dangerous, reason).
    """
    if depth > 5:
        # Fail closed: nesting too deep to analyze safely
        return True, "command nesting too deep to safely analyze (possible obfuscation)"

    i = 0
    while i < len(tokens):
        token = tokens[i]

        # Skip shell operators and empty tokens
        if not token or token in SHELL_OPERATORS:
            i += 1
            continue

        # ── Wrapper commands (sudo, env, nice, …) ────────────────────────────
        if token in WRAPPER_COMMANDS:
            i += 1
            continue

        # ── Quoted-command wrappers (watch, strace, ltrace) ──────────────────
        # These execute their first non-flag positional argument as a command
        # string and must be retokenized.
        if token in QUOTED_COMMAND_WRAPPERS:
            j = i + 1
            while j < len(tokens):
                arg = tokens[j]
                if not arg or arg in SHELL_OPERATORS:
                    break
                if arg.startswith("-"):
                    j += 1
                    continue
                # First non-flag positional argument is the command to execute
                inner_tokens = _tokenize(arg)
                dangerous, reason = _check_tokens(inner_tokens, cwd, depth + 1)
                if dangerous:
                    return True, reason
                break
            i += 1
            continue

        # ── Shell invocations: bash -c "..." ──────────────────────────────────
        if token in SHELL_COMMANDS:
            j = i + 1
            while j < len(tokens):
                if tokens[j] == "-c" and j + 1 < len(tokens):
                    inner_tokens = _tokenize(tokens[j + 1])
                    dangerous, reason = _check_tokens(inner_tokens, cwd, depth + 1)
                    if dangerous:
                        return True, reason
                    break
                elif tokens[j].startswith("-"):
                    j += 1
                else:
                    break
            i += 1
            continue

        # ── find -exec rm {} \; ───────────────────────────────────────────────
        if token == "find":
            j = i + 1
            while j < len(tokens):
                if tokens[j] in FIND_EXEC_FLAGS and j + 1 < len(tokens):
                    end = j + 2
                    while end < len(tokens) and tokens[end] not in (r"\;", "+", ";"):
                        end += 1
                    exec_tokens = tokens[j + 1 : end]
                    dangerous, reason = _check_tokens(exec_tokens, cwd, depth + 1)
                    if dangerous:
                        return True, reason
                j += 1
            i += 1
            continue

        # ── xargs / parallel ──────────────────────────────────────────────────
        if token in DELEGATION_COMMANDS:
            if i + 1 < len(tokens):
                dangerous, reason = _check_tokens(tokens[i + 1 :], cwd, depth + 1)
                if dangerous:
                    return True, reason
            i += 1
            continue

        # ── AWS CLI ───────────────────────────────────────────────────────────
        if token == "aws":
            parts: list[str] = []
            j = i + 1
            while j < len(tokens) and tokens[j].startswith("--"):
                j += 1
            while j < len(tokens) and not tokens[j].startswith("-") and len(parts) < 3:
                parts.append(tokens[j])
                j += 1
            for length in range(len(parts), 0, -1):
                sub = " ".join(parts[:length])
                if sub in AWS_DESTRUCTIVE_SUBCOMMANDS:
                    return True, f"AWS CLI destructive operation: aws {sub}"
            i += 1
            continue

        # ── Docker ────────────────────────────────────────────────────────────
        if token == "docker":
            if i + 1 < len(tokens):
                sub1 = tokens[i + 1]
                rest = tokens[i + 2:]
                # Check compound form: docker <object> <operation> (e.g. docker container rm)
                if i + 2 < len(tokens):
                    compound = f"{sub1} {tokens[i + 2]}"
                    if compound in DOCKER_DESTRUCTIVE_COMPOUND:
                        return True, f"Docker destructive operation: docker {compound}"
                # Check simple legacy form: docker rm, docker rmi
                if sub1 in DOCKER_DESTRUCTIVE_SUBCOMMANDS:
                    return True, f"Docker destructive operation: docker {sub1}"
                # Check docker compose down -v (removes volumes)
                if sub1 == "compose" and i + 2 < len(tokens):
                    compose_sub = tokens[i + 2]
                    if compose_sub == "down" and "-v" in rest:
                        return True, "docker compose down -v removes volumes with data loss risk"
                    if compose_sub == "rm":
                        return True, "docker compose rm removes stopped containers"
                # Check docker context rm
                if sub1 == "context" and i + 2 < len(tokens) and tokens[i + 2] == "rm":
                    return True, "docker context rm removes Docker contexts"
                # Check docker swarm leave --force
                if sub1 == "swarm" and i + 2 < len(tokens) and tokens[i + 2] == "leave":
                    if "--force" in rest:
                        return True, "docker swarm leave --force forcibly removes node from swarm"
            i += 1
            continue

        # ── Git ───────────────────────────────────────────────────────────────
        if token == "git":
            if i + 1 < len(tokens):
                sub = tokens[i + 1]
                rest = tokens[i + 2 :]
                if sub == "reset" and "--hard" in rest:
                    return True, "git reset --hard discards all local changes"
                if sub == "clean":
                    # Allow dry-run flags: -n / --dry-run
                    if "-n" not in rest and "--dry-run" not in rest:
                        return True, "git clean removes untracked files (use -n for dry run first)"
                # Block force push operations
                if sub == "push":
                    if "--force" in rest or "-f" in rest:
                        return True, "git push --force overwrites remote history (destructive)"
                    if "--force-with-lease" in rest:
                        return True, "git push --force-with-lease can overwrite remote history"
                    if "--delete" in rest:
                        return True, "git push --delete removes remote branch/tag"
                # Block forced branch deletion
                if sub == "branch":
                    if "-D" in rest:
                        return True, "git branch -D forcibly deletes branch without checks"
                # Block tag deletion
                if sub == "tag":
                    if "-d" in rest or "--delete" in rest:
                        return True, "git tag -d deletes tag"
                # Block forced checkout
                if sub == "checkout":
                    if "-f" in rest or "--force" in rest:
                        return True, "git checkout -f discards local changes forcibly"
                # Block rebase operations
                if sub == "rebase":
                    return True, "git rebase rewrites commit history (potentially destructive)"
                # Block history rewriting tools
                if sub in ("filter-branch", "filter-repo"):
                    return True, f"git {sub} rewrites repository history (highly destructive)"
                # Block reflog expiration
                if sub == "reflog":
                    if "expire" in rest:
                        return True, "git reflog expire deletes recovery references"
                # Block reference deletion via update-ref
                if sub == "update-ref":
                    if "-d" in rest or "--delete" in rest:
                        return True, "git update-ref -d deletes git references directly"
                # Block git add (stages changes)
                if sub == "add":
                    return True, "git add stages changes to the index"
                # Block git commit (creates commits)
                if sub == "commit":
                    return True, "git commit creates new commits in the repository"
            i += 1
            continue

        # ── File reading commands (check for sensitive files) ─────────────────
        if token in FILE_READING_COMMANDS:
            j = i + 1
            while j < len(tokens):
                arg = tokens[j]
                if not arg or arg in SHELL_OPERATORS:
                    break
                if arg.startswith("-"):
                    j += 1
                    continue
                # Check if the file path matches sensitive patterns
                arg_lower = arg.lower()
                for pattern in SENSITIVE_FILE_PATTERNS:
                    if pattern in arg_lower or arg_lower.endswith(pattern):
                        return True, f"attempt to read sensitive file: {arg!r}"
                j += 1
            i += 1
            continue

        # ── Path-sensitive commands ───────────────────────────────────────────
        if token in PATH_SENSITIVE_COMMANDS:
            j = i + 1
            while j < len(tokens):
                arg = tokens[j]
                if not arg or arg in SHELL_OPERATORS:
                    break
                if arg == "--":
                    j += 1
                    continue
                if arg.startswith("-"):
                    j += 1
                    continue
                outside, reason = _is_outside_cwd(arg, cwd)
                if outside:
                    return True, f"{token!r} targets path outside working directory — {reason}"
                j += 1
            i += 1
            continue

        i += 1

    return False, ""


# ─── Entry Point ───────────────────────────────────────────────────────────────


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # Non-blocking: malformed input, allow through

    if input_data.get("tool_name") != "Bash":
        sys.exit(0)

    command: str = input_data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    cwd = os.environ.get("CLAUDE_CWD", os.getcwd())
    tokens = _tokenize(command)
    dangerous, reason = _check_tokens(tokens, cwd)

    if dangerous:
        print(f"BLOCKED: {reason}", file=sys.stderr)
        print(f"Command : {command}", file=sys.stderr)
        print(f"CWD     : {cwd}", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
