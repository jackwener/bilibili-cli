"""Shared helpers for CLI command modules."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from typing import NoReturn

import click
import yaml
from rich.console import Console

from .. import auth
from ..exceptions import BiliError, InvalidBvidError

console = Console(stderr=True)
OutputFormat = str | None
_OUTPUT_ENV = "OUTPUT"
_SCHEMA_VERSION = "1"


def setup_logging(verbose: bool):
    """Configure global logging based on CLI verbosity."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(name)s: %(message)s")


def run(coro):
    """Bridge async coroutine into synchronous click command."""
    return asyncio.run(coro)


def resolve_output_format(*, as_json: bool = False, as_yaml: bool = False) -> OutputFormat:
    """Resolve mutually exclusive machine-readable output flags."""
    if as_json and as_yaml:
        exit_error("不能同时使用 --json 和 --yaml。")
    if as_yaml:
        return "yaml"
    if as_json:
        return "json"
    output_mode = os.getenv(_OUTPUT_ENV, "auto").strip().lower()
    if output_mode == "yaml":
        return "yaml"
    if output_mode == "json":
        return "json"
    if output_mode == "rich":
        return None
    if not sys.stdout.isatty():
        return "yaml"
    return None


def emit_structured(data: object, output_format: OutputFormat) -> bool:
    """Serialize data for machine-readable output and report whether emission happened."""
    if output_format == "json":
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
        return True
    if output_format == "yaml":
        click.echo(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))
        return True
    return False


def success_payload(data: object) -> dict[str, object]:
    """Wrap structured success data in the shared agent schema."""
    return {
        "ok": True,
        "schema_version": _SCHEMA_VERSION,
        "data": data,
    }


def error_payload(code: str, message: str, *, details: object | None = None) -> dict[str, object]:
    """Wrap structured error data in the shared agent schema."""
    error: dict[str, object] = {
        "code": code,
        "message": message,
    }
    if details is not None:
        error["details"] = details
    return {
        "ok": False,
        "schema_version": _SCHEMA_VERSION,
        "error": error,
    }


def exit_error(message: str) -> NoReturn:
    """Print an error message and exit with non-zero status."""
    console.print(f"[red]❌ {message}[/red]")
    sys.exit(1)


def run_or_exit(coro, action: str):
    """Run async call and convert unexpected errors to CLI-friendly failures."""
    try:
        return run(coro)
    except BiliError as e:
        exit_error(f"{action}: {e}")
    except Exception as e:
        exit_error(f"{action}: {e}")


def _to_int(value: object, default: int = 0) -> int:
    """Best-effort convert value to int for display-oriented formatting."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return default
    return default


def format_duration(seconds: object) -> str:
    """Format seconds into MM:SS or HH:MM:SS."""
    seconds_int = _to_int(seconds, default=0)
    if seconds_int < 0:
        seconds_int = 0
    if seconds_int >= 3600:
        h, rem = divmod(seconds_int, 3600)
        m, s = divmod(rem, 60)
        return f"{h}:{m:02d}:{s:02d}"
    m, s = divmod(seconds_int, 60)
    return f"{m:02d}:{s:02d}"


def format_count(n: object) -> str:
    """Format large numbers with 万 suffix."""
    value = _to_int(n, default=0)
    if value >= 10000:
        return f"{value / 10000:.1f}万"
    return str(value)


def get_credential(mode: auth.AuthMode = "read"):
    """Read credential from configured auth strategy."""
    return auth.get_credential(mode=mode)


def clear_credential():
    """Remove saved credential."""
    return auth.clear_credential()


def qr_login():
    """Return login coroutine for QR login flow."""
    return auth.qr_login()


def print_login_required(message: str | None = None):
    """Print a standard login-required warning message."""
    if message:
        console.print(f"[yellow]⚠️  {message}[/yellow]")
        return
    console.print("[yellow]⚠️  需要登录。使用 [bold]bili login[/bold] 登录。[/yellow]")


def require_login(require_write: bool = False, message: str | None = None):
    """Require login credential and optional write capability."""
    mode: auth.AuthMode = "write" if require_write else "read"
    cred = get_credential(mode=mode)
    if cred:
        return cred

    if require_write:
        # Diagnose a common case: saved session exists but lacks bili_jct.
        saved = get_credential(mode="optional")
        if saved and getattr(saved, "sessdata", "") and not getattr(saved, "bili_jct", ""):
            exit_error("当前登录凭证不支持写操作（缺少 bili_jct）。请执行 bili login 重新登录。")

    print_login_required(message)
    sys.exit(1)


def run_optional(coro, action: str):
    """Run optional sub-request and print warning on failure."""
    try:
        return run(coro)
    except BiliError as e:
        console.print(f"[yellow]⚠️  {action}: {e}[/yellow]")
    except Exception as e:
        console.print(f"[yellow]⚠️  {action}: {e}[/yellow]")
    return None


def extract_bvid_or_exit(bv_or_url: str) -> str:
    """Extract BV ID from input; print a user-friendly error on failure."""
    from .. import client

    try:
        return client.extract_bvid(bv_or_url)
    except (InvalidBvidError, ValueError) as e:
        exit_error(str(e))
